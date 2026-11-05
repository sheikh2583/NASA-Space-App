import pytest
from scripts.export_hosted_demo import record_end, validate_record_dates


class Client:
    def __init__(self, value):
        self.value = value

    def get(self, path):
        assert path == "/health"
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return {"data_through": self.value}


def test_record_end_comes_from_runtime_not_hardcoded_day():
    assert record_end(Client("2026-11-03")) == "2026-11-03"
    assert record_end(Client("2026-12-01")) == "2026-12-01"


@pytest.mark.parametrize("value", [None, "2026-02-30", "2026-11-3", "bad"])
def test_invalid_record_metadata_is_rejected(value):
    with pytest.raises((ValueError, TypeError)):
        record_end(Client(value))


def test_export_rejects_response_date_mismatch():
    with pytest.raises(ValueError, match="disagrees"):
        validate_record_dates({"season": {"data_through": "2026-11-02"}}, "2026-11-03")
    validate_record_dates({"outlook": {"current_status": {"data_through": "2026-11-03"}}}, "2026-11-03")
