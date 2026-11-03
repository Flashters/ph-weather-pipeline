import pandas as pd
import pytest
from etl import validate

def test_validate_drops_bad_rows():
    """Verify data quality gate filters out impossible or null values."""
    raw_df = pd.DataFrame({
        "temp_c": [30.0, 999.0, None, 25.0, 32.0, -15.0],
        "humidity": [80.0, 50.0, 70.0, 120.0, 60.0, 40.0],
        "rain_mm": [0.0, 0.0, 0.0, 0.0, -5.0, 0.0]
    })
    
    validated_df = validate(raw_df)
    # Only row 0 (30°C, 80% humidity, 0mm rain) is valid
    assert len(validated_df) == 1
    assert validated_df.iloc[0]["temp_c"] == 30.0

def test_validate_empty_raises_error():
    """Verify that an empty valid dataset aborts the ETL pipeline."""
    raw_df = pd.DataFrame({
        "temp_c": [999.0],
        "humidity": [150.0],
        "rain_mm": [-10.0]
    })
    with pytest.raises(ValueError, match="No valid rows - aborting load"):
        validate(raw_df)