"""
Unit Tests for Player Trajectories
===================================
Verifies path construction, chronological sorting, human/bot styling,
and prevention of player cross-contamination.
"""

import pandas as pd
import pytest
from src.player_paths import create_player_trajectories, HUMAN_COLOR, BOT_COLOR


def test_empty_dataframe_returns_empty_traces():
    """Verify empty input does not crash."""
    traces = create_player_trajectories(pd.DataFrame())
    assert traces == []


def test_trajectory_separation_and_styling():
    """Verify human vs bot colors and independent paths."""
    df = pd.DataFrame({
        'user_id': ['human-uuid-1', 'human-uuid-1', 'bot-100', 'bot-100'],
        'match_id': ['m1', 'm1', 'm1', 'm1'],
        'event': ['Position', 'Position', 'BotPosition', 'BotPosition'],
        'x': [10.0, 20.0, 30.0, 40.0],
        'y': [100.0, 100.0, 100.0, 100.0],
        'z': [10.0, 20.0, 30.0, 40.0],
        'pixel_x': [100.0, 200.0, 300.0, 400.0],
        'pixel_y': [100.0, 200.0, 300.0, 400.0],
        'ts_sec': [10, 20, 12, 22],
        'is_human': [True, True, False, False],
        'is_bot': [False, False, True, True]
    })

    traces = create_player_trajectories(df, show_markers=True)
    assert len(traces) > 0

    # Locate human trajectory trace
    human_line = [t for t in traces if t.name and 'Human' in t.name][0]
    assert human_line.line.color == HUMAN_COLOR

    # Locate bot trajectory trace
    bot_line = [t for t in traces if t.name and 'Bot' in t.name][0]
    assert bot_line.line.color == BOT_COLOR


def test_chronological_ordering():
    """Verify that points in path are strictly sorted by timestamp."""
    # Input provided in reverse chronological order
    df = pd.DataFrame({
        'user_id': ['human-uuid-1', 'human-uuid-1', 'human-uuid-1'],
        'match_id': ['m1', 'm1', 'm1'],
        'event': ['Position', 'Position', 'Position'],
        'x': [30.0, 10.0, 20.0],
        'y': [100.0, 100.0, 100.0],
        'z': [30.0, 10.0, 20.0],
        'pixel_x': [300.0, 100.0, 200.0],
        'pixel_y': [300.0, 100.0, 200.0],
        'ts_sec': [30, 10, 20],  # Out of order
        'is_human': [True, True, True],
        'is_bot': [False, False, False]
    })

    traces = create_player_trajectories(df)
    line_trace = [t for t in traces if t.name and 'Human' in t.name][0]

    # Verify x values are in chronological order (100 -> 200 -> 300)
    assert list(line_trace.x) == [100.0, 200.0, 300.0]
