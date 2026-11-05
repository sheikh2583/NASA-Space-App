from ws2_platform.tests.conftest import tiny_request


def test_record_end_and_complete_week_profile_cutoff_are_distinct(tiny_api):
    health = tiny_api.get("/health").json()
    response = tiny_api.post("/aoi/season", json=tiny_request("pb"))
    assert response.status_code == 200
    profile = response.json()
    assert profile["record_data_through"] == health["data_through"]
    assert profile["data_through"] <= profile["record_data_through"]
