"""
Unit Tests for Timeline Playback Controls
==========================================
Verifies slider types, zero duration handling, formatting, and playback math.
"""

import pandas as pd
import pytest
from components.timeline import format_seconds, render_timeline_controls


def test_format_seconds():
    """Verify MM:SS string formatting."""
    assert format_seconds(0) == "00:00"
    assert format_seconds(59) == "00:59"
    assert format_seconds(60) == "01:00"
    assert format_seconds(125.4) == "02:05"
    assert format_seconds(622) == "10:22"
    assert format_seconds(-5) == "00:00"


def test_empty_dataframe_returns_cleanly():
    """Verify empty DataFrame does not crash."""
    filtered_df, curr, max_t = render_timeline_controls(pd.DataFrame())
    assert filtered_df.empty
    assert curr == 0
    assert max_t == 0


def test_zero_duration_match_returns_cleanly():
    """Verify single-event match with 0s elapsed time does not crash slider."""
    df = pd.DataFrame({
        'match_id': ['m1', 'm1'],
        'user_id': ['u1', 'u1'],
        'elapsed_sec': [0, 0],
        'event': ['Position', 'Position']
    })
    filtered_df, curr, max_t = render_timeline_controls(df)
    assert len(filtered_df) == 2
    assert curr == 0
    assert max_t == 0
