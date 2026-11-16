from etl import validate


def test_validate_valid_payload():
    sample_payload = {
        "hourly": {
            "time": ["2026-11-16T00:00"],
            "temperature_2m": [28.5],
            "relative_humidity_2m": [80],
            "precipitation": [0.0],
        }
    }
    assert validate(sample_payload) is True


def test_validate_invalid_payload():
    # Missing required keys
    invalid_payload = {
        "hourly": {
            "time": ["2026-11-16T00:00"],
        }
    }
    assert validate(invalid_payload) is False
    assert validate({}) is False
    assert validate(None) is False
