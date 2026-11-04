"""Production training commands must reject CPU mode before doing any work."""
import sys
import pytest
from common import compute
from scripts import prepare_training, run_pipeline, workflow
from ws1_harmonize import run as harmonize
from ws4_outlook import run as outlook


def test_workflow_cli_rejects_cpu(capsys):
    with pytest.raises(SystemExit) as error:
        workflow.main(['train', '--backend', 'cpu'])
    assert error.value.code == 2
    assert 'invalid choice' in capsys.readouterr().err


def test_pipeline_cli_rejects_cpu(monkeypatch, capsys):
    monkeypatch.setattr(sys, 'argv', ['run_pipeline.py', '--backend', 'cpu'])
    with pytest.raises(SystemExit) as error:
        run_pipeline.main()
    assert error.value.code == 2
    assert 'invalid choice' in capsys.readouterr().err


def test_workflow_function_rejects_cpu_before_subprocess(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail('CPU training must not reach a subprocess')
    monkeypatch.setattr(workflow, 'run', unexpected)
    with pytest.raises(ValueError, match='requires the CUDA backend'):
        workflow.train(False, None, backend='cpu')


@pytest.mark.parametrize('module, command', [(harmonize, 'model'), (outlook, 'drift'), (outlook, 'outlook')])
def test_direct_training_cli_rejects_inherited_cpu(monkeypatch, module, command):
    monkeypatch.setenv('FIRESENSE_BACKEND', 'cpu')
    with pytest.raises(RuntimeError, match='Training requires CUDA'):
        module.main(command)


def test_direct_readiness_rejects_cpu(monkeypatch):
    monkeypatch.setenv('FIRESENSE_BACKEND', 'cpu')
    with pytest.raises(RuntimeError, match='Training requires CUDA'):
        prepare_training.main()


def test_direct_model_defaults_to_cuda_before_fitting(monkeypatch):
    monkeypatch.setenv('FIRESENSE_BACKEND', 'cuda')
    monkeypatch.delenv('FIRESENSE_BACKEND')
    monkeypatch.setenv('FIRESENSE_THREADS', '8')
    calls = []
    monkeypatch.setattr(harmonize, 'step_model', lambda: calls.append(compute.backend()))
    harmonize.main('model')
    assert calls == ['cuda']
