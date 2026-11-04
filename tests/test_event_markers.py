"""
Unit Tests for Event Markers
=============================
Verifies rendering and filtering of discrete combat, loot, and storm markers.
"""

import pandas as pd
import pytest
from src.event_markers import create_event_markers, EVENT_STYLES


def test_empty_dataframe_returns_empty_markers():
    """Verify empty input handling."""
    traces = create_event_markers(pd.DataFrame())
    assert traces == []


def test_filters_out_positional_events():
    """Verify that Position and BotPosition do not generate discrete event markers."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2'],
        'match_id': ['m1', 'm1'],
        'event': ['Position', 'BotPosition'],
        'pixel_x': [100.0, 200.0],
        'pixel_y': [100.0, 200.0],
        'x': [10.0, 20.0],
        'y': [50.0, 50.0],
        'z': [10.0, 20.0],
        'player_type': ['Human', 'Bot']
    })
    traces = create_event_markers(df)
    assert traces == []


def test_renders_discrete_event_categories():
    """Verify each discrete event gets an appropriately styled marker trace."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2', 'u3', 'u4'],
        'match_id': ['m1', 'm1', 'm1', 'm1'],
        'event': ['Kill', 'Killed', 'Loot', 'KilledByStorm'],
        'pixel_x': [100.0, 200.0, 300.0, 400.0],
        'pixel_y': [100.0, 200.0, 300.0, 400.0],
        'x': [10.0, 20.0, 30.0, 40.0],
        'y': [50.0, 50.0, 50.0, 50.0],
        'z': [10.0, 20.0, 30.0, 40.0],
        'player_type': ['Human', 'Human', 'Human', 'Human']
    })

    traces = create_event_markers(df)
    trace_names = [t.name for t in traces]

    assert EVENT_STYLES['Kill']['name'] in trace_names
    assert EVENT_STYLES['Killed']['name'] in trace_names
    assert EVENT_STYLES['Loot']['name'] in trace_names
    assert EVENT_STYLES['KilledByStorm']['name'] in trace_names


def test_selective_event_filtering():
    """Verify active_event_types parameter restricts traces."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2'],
        'match_id': ['m1', 'm1'],
        'event': ['Kill', 'Loot'],
        'pixel_x': [100.0, 200.0],
        'pixel_y': [100.0, 200.0],
        'x': [10.0, 20.0],
        'y': [50.0, 50.0],
        'z': [10.0, 20.0],
        'player_type': ['Human', 'Human']
    })

    traces = create_event_markers(df, active_event_types=['Loot'])
    assert len(traces) == 1
    assert traces[0].name == EVENT_STYLES['Loot']['name']
