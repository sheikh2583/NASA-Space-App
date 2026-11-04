import subprocess
from types import SimpleNamespace
import pytest
from scripts import bootstrap


class StoppedServer:
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def connect_ex(self, address):
        return 1


@pytest.fixture(autouse=True)
def isolate_local_ports(monkeypatch):
    monkeypatch.setattr(bootstrap.socket, 'socket', StoppedServer)


def test_missing_cuda_driver_stops_before_installing(monkeypatch):
    monkeypatch.setattr(bootstrap.sys, 'prefix', 'test-venv')
    monkeypatch.setattr(bootstrap.shutil, 'which', lambda name: None if name == 'nvidia-smi' else name)
    monkeypatch.setattr(bootstrap.subprocess, 'check_output', lambda *a, **k: 'v22.12.0')
    calls = []
    monkeypatch.setattr(bootstrap, 'run', lambda *args: calls.append(args))
    with pytest.raises(RuntimeError, match='driver/nvidia-smi'):
        bootstrap.main([])
    assert calls == []


def test_pinned_failure_is_not_silently_replaced_by_unpinned_install(monkeypatch):
    monkeypatch.setattr(bootstrap.sys, 'prefix', 'test-venv')
    monkeypatch.setattr(bootstrap.shutil, 'which', lambda name: name)
    monkeypatch.setattr(bootstrap.subprocess, 'check_output', lambda *a, **k: 'v22.12.0')
    calls = []
    def run(*args):
        calls.append(args)
        if 'requirements.lock.txt' in args:
            raise subprocess.CalledProcessError(1, args)
    monkeypatch.setattr(bootstrap, 'run', run)
    with pytest.raises(RuntimeError, match='Pinned dependency installation failed'):
        bootstrap.main(['--ui-only'])
    assert not any('requirements.txt' in args for args in calls)


def test_running_vite_stops_setup_before_package_changes(monkeypatch):
    monkeypatch.setattr(bootstrap.sys, 'prefix', 'test-venv')
    monkeypatch.setattr(bootstrap.shutil, 'which', lambda name: name)
    monkeypatch.setattr(bootstrap.subprocess, 'check_output', lambda *a, **k: 'v22.12.0')
    monkeypatch.setattr(StoppedServer, 'connect_ex', lambda *args: 0)
    calls = []
    monkeypatch.setattr(bootstrap, 'run', lambda *args: calls.append(args))
    with pytest.raises(RuntimeError, match='Stop the Vite development server'):
        bootstrap.main(['--ui-only'])
    assert calls == []


def test_running_preview_stops_full_setup_before_package_changes(monkeypatch):
    monkeypatch.setattr(bootstrap.sys, 'prefix', 'test-venv')
    monkeypatch.setattr(bootstrap.shutil, 'which', lambda name: name)
    monkeypatch.setattr(bootstrap.subprocess, 'check_output', lambda *a, **k: 'v22.12.0')
    monkeypatch.setattr(StoppedServer, 'connect_ex', lambda self, address: 0 if address[1] == 4173 else 1)
    calls = []
    monkeypatch.setattr(bootstrap, 'run', lambda *args: calls.append(args))
    with pytest.raises(RuntimeError, match='preview server on port 4173'):
        bootstrap.main([])
    assert calls == []


def test_training_only_needs_no_node_and_preserves_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(bootstrap.sys, 'prefix', 'test-venv')
    monkeypatch.setattr(bootstrap, 'ROOT', tmp_path)
    monkeypatch.setattr(bootstrap.shutil, 'which', lambda name: name if name == 'nvidia-smi' else None)
    monkeypatch.setattr(StoppedServer, 'connect_ex', lambda *args: 0)
    (tmp_path / '.env').write_text('EXISTING=preserve\n')
    calls = []
    monkeypatch.setattr(bootstrap, 'run', lambda *args: calls.append(args))
    bootstrap.main(['--training-only', '--gpu-id', '1', '--threads', '4'])
    assert any('requirements-cuda.txt' in args for args in calls)
    assert any('gpu-check' in args and '1' in args and '4' in args for args in calls)
    assert not any('ci' in args or 'node' in args for args in calls)
    assert (tmp_path / '.env').read_text() == 'EXISTING=preserve\n'
    assert not (tmp_path / 'ws5_frontend').exists()


@pytest.mark.parametrize('libc,version', [('musl', '1.2'), ('glibc', '2.27')])
def test_linux_training_rejects_incompatible_libc_before_install(monkeypatch, libc, version):
    monkeypatch.setattr(bootstrap, 'sys', SimpleNamespace(platform='linux'))
    monkeypatch.setattr(bootstrap.platform, 'machine', lambda: 'x86_64')
    monkeypatch.setattr(bootstrap.platform, 'libc_ver', lambda: (libc, version))
    with pytest.raises(RuntimeError, match='glibc 2.28'):
        bootstrap.check_linux_runtime()


def test_linux_training_reports_missing_openmp_without_fitting(monkeypatch):
    import ctypes
    monkeypatch.setattr(bootstrap, 'sys', SimpleNamespace(platform='linux'))
    monkeypatch.setattr(bootstrap.platform, 'machine', lambda: 'x86_64')
    monkeypatch.setattr(bootstrap.platform, 'libc_ver', lambda: ('glibc', '2.36'))
    def missing(name):
        raise OSError('not installed')
    monkeypatch.setattr(ctypes, 'CDLL', missing)
    with pytest.raises(RuntimeError, match='sudo apt-get install libgomp1'):
        bootstrap.check_linux_runtime()


def test_linux_host_check_loads_only_openmp(monkeypatch):
    import ctypes
    monkeypatch.setattr(bootstrap, 'sys', SimpleNamespace(platform='linux'))
    monkeypatch.setattr(bootstrap.platform, 'machine', lambda: 'x86_64')
    monkeypatch.setattr(bootstrap.platform, 'libc_ver', lambda: ('glibc', '2.36'))
    loaded = []
    monkeypatch.setattr(ctypes, 'CDLL', loaded.append)
    bootstrap.check_linux_runtime()
    assert loaded == ['libgomp.so.1']
