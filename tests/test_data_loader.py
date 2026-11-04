"""
Unit Tests for Data Loader & Schema Validation
===============================================
Verifies parquet reading, bytes decoding, timestamp reconstruction,
human/bot identification, and validation functions.
"""

import os
import glob
import pytest
import pandas as pd
from src.data_loader import (
    normalize_dataframe,
    load_single_file,
    load_match_telemetry,
    decode_event
)
from src.validators import (
    validate_schema,
    validate_events,
    validate_coordinates,
    is_human_user
)

DATA_DIR = r"C:\Users\Sanjay gm\Downloads\LILA GAMES\player_data"


def test_decode_event():
    """Verify bytes decoding logic."""
    assert decode_event(b'Position') == 'Position'
    assert decode_event(b'Kill') == 'Kill'
    assert decode_event('Loot') == 'Loot'


def test_human_bot_classification():
    """Verify UUID vs numeric player ID classification."""
    # Human UUID
    assert is_human_user("f4e072fa-b7af-4761-b567-1d95b7ad0108") is True
    assert is_human_user("0019c582-574d-4a53-9f77-554519b75b4c") is True
    
    # Bot numeric IDs
    assert is_human_user("1440") is False
    assert is_human_user("382") is False
    assert is_human_user("1455") is False


def test_normalize_dataframe():
    """Verify dataframe normalization pipeline."""
    raw_df = pd.DataFrame({
        'user_id': ['f4e072fa-b7af-4761-b567-1d95b7ad0108', '1440'],
        'match_id': ['match1.nakama-0', 'match1.nakama-0'],
        'map_id': ['AmbroseValley', 'AmbroseValley'],
        'x': [-301.45, -280.85],
        'y': [124.97, 121.62],
        'z': [-355.55, -323.35],
        'ts': pd.to_datetime(['1970-01-21 11:52:34.537', '1970-01-21 11:52:34.557']),
        'event': [b'Position', b'BotPosition']
    })

    cleaned = normalize_dataframe(raw_df, compute_coords=True)

    # Check decoded event
    assert cleaned['event'].tolist() == ['Position', 'BotPosition']

    # Check player type
    assert cleaned['player_type'].tolist() == ['Human', 'Bot']
    assert cleaned['is_human'].tolist() == [True, False]
    assert cleaned['is_bot'].tolist() == [False, True]

    # Check timestamp reconstruction in 2026
    assert cleaned['timestamp'].dt.year.tolist() == [2026, 2026]
    assert cleaned['timestamp'].dt.month.tolist() == [2, 2]

    # Check coordinates added
    assert 'pixel_x' in cleaned.columns
    assert 'pixel_y' in cleaned.columns
    assert round(cleaned.loc[0, 'pixel_x']) == 78
    assert round(cleaned.loc[0, 'pixel_y']) == 890


def test_load_real_sample_file():
    """Verify loading and parsing an actual telemetry file from the dataset."""
    sample_files = glob.glob(os.path.join(DATA_DIR, "February_10", "*.nakama-0"))
    assert len(sample_files) > 0, "No sample telemetry files found in February_10"

    df = load_single_file(sample_files[0], compute_coords=True)
    assert not df.empty

    is_valid_schema, errors = validate_schema(df)
    assert is_valid_schema, f"Schema validation failed: {errors}"

    is_valid_events, ev_errors = validate_events(df)
    assert is_valid_events, f"Event validation failed: {ev_errors}"

    is_valid_coords, coord_report = validate_coordinates(df)
    assert is_valid_coords, f"Coordinate bounds validation failed: {coord_report}"


def test_load_match_telemetry_elapsed_time():
    """Verify match telemetry consolidation and elapsed time calculation."""
    # Top match identified during discovery
    match_id = "fbbc5d02-dd79-42fb-bba5-d768023891c8"
    df = load_match_telemetry(match_id, DATA_DIR, compute_coords=True)
    
    assert not df.empty, f"No telemetry loaded for match {match_id}"
    assert 'elapsed_sec' in df.columns
    assert df['elapsed_sec'].min() == 0, "Elapsed time should start at 0 seconds"
    assert df['elapsed_sec'].max() > 0, "Match duration should be positive"
    assert df['user_id'].nunique() > 1, "Match should contain multiple participants"
