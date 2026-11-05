import ast
from pathlib import Path
import pytest
from ws4_outlook import alerts


def test_watch_promotes_to_high_and_high_hysteresis():
    assert alerts.alert_level([85, 95], [80, 92], "skill")["level"] == "high"
    assert alerts.alert_level([95, 85], [92, 70], "skill")["level"] == "high"
    assert alerts.alert_level([95, 79], [92, 70], "skill")["level"] == "none"
    assert alerts.alert_level([95], [70], "skill")["level"] == "watch"


@pytest.mark.parametrize("points,lowers", [([90], []), ([101], [90]), ([90], [91]),
                                         ([float("nan")], [90]), ([90], [None])])
def test_invalid_uncertainty_inputs_are_rejected(points, lowers):
    with pytest.raises(ValueError):
        alerts.alert_level(points, lowers, "skill")


def test_unvalidated_forecast_and_absent_bounds_are_off():
    assert alerts.alert_level([95], [95], "no_demonstrated_skill")["level"] == "none"
    assert alerts.no_forecast_bounds()["level"] == "none"


def test_batch_caller_cannot_substitute_observed_status_for_forecast():
    tree = ast.parse(Path("ws4_outlook/run.py").read_text())
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "step_outlook")
    calls = [node.func.attr for node in ast.walk(fn)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
             and isinstance(node.func.value, ast.Name) and node.func.value.id == "alerts"]
    assert calls == ["no_forecast_bounds"]
