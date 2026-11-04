import json
import sys
from types import SimpleNamespace
import pytest
from common import compute


def test_invalid_compute_settings_are_rejected(monkeypatch):
    monkeypatch.setenv("FIRESENSE_BACKEND", "magic")
    with pytest.raises(ValueError):
        compute.backend()
    monkeypatch.setenv("FIRESENSE_THREADS", "0")
    with pytest.raises(ValueError):
        compute.threads()


def test_cuda_request_cannot_silently_become_cpu(monkeypatch):
    monkeypatch.setenv("FIRESENSE_GPU_ID", "0")

    class CpuBooster:
        def save_config(self):
            return json.dumps({"learner": {"generic_param": {"device": "cpu"}}})

    with pytest.raises(RuntimeError, match="refusing CPU fallback"):
        compute.assert_cuda(CpuBooster())


def test_probe_failure_restores_run_log_without_writing(monkeypatch, tmp_path):
    path = tmp_path / 'cuda-fits.jsonl'
    monkeypatch.setenv('FIRESENSE_COMPUTE_LOG', str(path))
    monkeypatch.setitem(sys.modules, 'xgboost', SimpleNamespace(build_info=lambda: {'USE_CUDA': True}))
    def failed_fit(*args, **kwargs):
        assert 'FIRESENSE_COMPUTE_LOG' not in compute.os.environ
        raise RuntimeError('GPU probe failed')
    monkeypatch.setattr(compute, 'train_cuda', failed_fit)
    with pytest.raises(RuntimeError, match='GPU probe failed'):
        compute.probe_cuda()
    assert compute.os.environ['FIRESENSE_COMPUTE_LOG'] == str(path)
    assert not path.exists()
