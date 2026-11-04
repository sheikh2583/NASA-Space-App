import subprocess
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
