"""
Unit Tests for Game Analytics Computations
===========================================
Verifies quadrant spatial partitioning, human vs bot summaries, and pacing.
"""

import pandas as pd
import pytest
from src.analytics import (
    compute_quadrant_distribution,
    compute_human_bot_summary,
    compute_temporal_event_distribution
)


def test_compute_quadrant_distribution():
    """Verify quadrant assignment logic."""
    df = pd.DataFrame({
        'u': [0.2, 0.8, 0.2, 0.8],
        'v': [0.8, 0.8, 0.2, 0.2],
        'event': ['Kill', 'Kill', 'Kill', 'Kill']
    })
    quads = compute_quadrant_distribution(df, ['Kill'])
    assert len(quads) == 4
    quad_dict = dict(zip(quads['Quadrant'], quads['Count']))
    assert quad_dict.get('Northwest (NW)') == 1
    assert quad_dict.get('Northeast (NE)') == 1
    assert quad_dict.get('Southwest (SW)') == 1
    assert quad_dict.get('Southeast (SE)') == 1


def test_compute_human_bot_summary():
    """Verify entity combat calculations."""
    df = pd.DataFrame({
        'user_id': ['h1-uuid-0000000000000000000000', 'bot-1'],
        'is_human': [True, False],
        'is_bot': [False, True],
        'event': ['BotKill', 'Position']
    })
    summary = compute_human_bot_summary(df)
    assert summary['human_count'] == 1
    assert summary['bot_count'] == 1
    assert summary['human_kills'] == 1
    assert summary['bot_deaths'] == 1


def test_temporal_event_distribution():
    """Verify temporal binning."""
    df = pd.DataFrame({
        'elapsed_sec': [5, 12, 35, 40],
        'event': ['Loot', 'Loot', 'BotKill', 'Kill']
    })
    temporal = compute_temporal_event_distribution(df, bin_size_sec=15)
    assert not temporal.empty
    assert 'time_bin' in temporal.columns
    assert 0 in temporal['time_bin'].values
    assert 30 in temporal['time_bin'].values
