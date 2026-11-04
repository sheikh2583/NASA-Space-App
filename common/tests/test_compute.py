import json
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
