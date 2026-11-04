"""
Unit Tests for Heatmap Generation
==================================
Verifies density calculation, empty handling, low variance handling, and stats.
"""

import pandas as pd
import pytest
from src.heatmaps import create_density_heatmap, get_heatmap_stats, HEATMAP_PRESETS


def test_empty_heatmap_returns_none():
    """Verify empty dataframe returns None without error."""
    assert create_density_heatmap(pd.DataFrame(), mode="Traffic") is None


def test_zero_variance_coordinates_returns_none():
    """Verify identical coordinate points do not crash contour matrix."""
    df = pd.DataFrame({
        'pixel_x': [100.0, 100.0, 100.0],
        'pixel_y': [200.0, 200.0, 200.0],
        'event': ['Position', 'Position', 'Position']
    })
    assert create_density_heatmap(df, mode="Traffic") is None


def test_valid_data_generates_histogram2d_contour():
    """Verify valid points create a Histogram2dContour trace."""
    df = pd.DataFrame({
        'pixel_x': [100.0, 200.0, 300.0, 400.0],
        'pixel_y': [150.0, 250.0, 350.0, 450.0],
        'event': ['Position', 'Position', 'Position', 'Position']
    })
    trace = create_density_heatmap(df, mode="Traffic")
    assert trace is not None
    assert trace.type == 'histogram2dcontour'


def test_heatmap_stats():
    """Verify stats generation."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2', 'u1'],
        'match_id': ['m1', 'm1', 'm1'],
        'event': ['BotKill', 'Kill', 'Position']
    })
    stats = get_heatmap_stats(df, mode="Kill")
    assert stats['sample_count'] == 2
    assert stats['unique_players'] == 2
