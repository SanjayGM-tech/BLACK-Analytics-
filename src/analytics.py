"""
Analytics & Statistical Computations for LILA BLACK Telemetry
==============================================================
Provides aggregation algorithms and chart data generators for:
- Spatial distribution by quadrant (NW, NE, SW, SE)
- Human vs. Bot performance metrics
- Combat and loot temporal progression
- Match duration distribution
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def compute_quadrant_distribution(df: pd.DataFrame, target_events: List[str]) -> pd.DataFrame:
    """
    Partition coordinates into 4 map quadrants (NW, NE, SW, SE) based on UV space (0.5 threshold).
    u < 0.5 is West, u >= 0.5 is East.
    v >= 0.5 is North, v < 0.5 is South.
    """
    if df.empty or 'u' not in df.columns or 'v' not in df.columns:
        return pd.DataFrame({'Quadrant': ['NW', 'NE', 'SW', 'SE'], 'Count': [0, 0, 0, 0]})

    subset = df[df['event'].isin(target_events)].dropna(subset=['u', 'v']).copy()
    if subset.empty:
        return pd.DataFrame({'Quadrant': ['NW', 'NE', 'SW', 'SE'], 'Count': [0, 0, 0, 0]})

    conditions = [
        (subset['u'] < 0.5) & (subset['v'] >= 0.5),  # NW
        (subset['u'] >= 0.5) & (subset['v'] >= 0.5), # NE
        (subset['u'] < 0.5) & (subset['v'] < 0.5),   # SW
        (subset['u'] >= 0.5) & (subset['v'] < 0.5),  # SE
    ]
    choices = ['Northwest (NW)', 'Northeast (NE)', 'Southwest (SW)', 'Southeast (SE)']
    subset['quadrant'] = np.select(conditions, choices, default='Central')

    quad_counts = subset['quadrant'].value_counts().reset_index()
    quad_counts.columns = ['Quadrant', 'Count']
    return quad_counts


def compute_human_bot_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comparative behavioral and combat statistics between humans and bots."""
    if df.empty:
        return {
            'human_count': 0, 'bot_count': 0,
            'human_kills': 0, 'bot_kills': 0,
            'human_deaths': 0, 'bot_deaths': 0,
            'human_loot': 0, 'bot_loot': 0
        }

    humans = df[df['is_human']]
    bots = df[df['is_bot']]

    human_kills = int(((humans['event'] == 'Kill') | (humans['event'] == 'BotKill')).sum())
    human_deaths = int(((humans['event'] == 'Killed') | (humans['event'] == 'BotKilled') | (humans['event'] == 'KilledByStorm')).sum())
    human_loot = int((humans['event'] == 'Loot').sum())

    bot_deaths = int((df['event'] == 'BotKill').sum()) # bot died to human
    bot_kills = int((df['event'] == 'BotKilled').sum()) # bot killed human

    return {
        'human_count': int(humans['user_id'].nunique()),
        'bot_count': int(bots['user_id'].nunique()),
        'human_movement_samples': len(humans[humans['event'] == 'Position']),
        'bot_movement_samples': len(bots[bots['event'] == 'BotPosition']),
        'human_kills': human_kills,
        'bot_kills': bot_kills,
        'human_deaths': human_deaths,
        'bot_deaths': bot_deaths,
        'human_loot': human_loot,
    }


def compute_temporal_event_distribution(df: pd.DataFrame, bin_size_sec: int = 15) -> pd.DataFrame:
    """Group events by elapsed match time intervals to analyze match pacing."""
    if df.empty or 'elapsed_sec' not in df.columns:
        return pd.DataFrame()

    df_valid = df.dropna(subset=['elapsed_sec']).copy()
    max_time = df_valid['elapsed_sec'].max()
    if max_time <= 0:
        return pd.DataFrame()

    df_valid['time_bin'] = (df_valid['elapsed_sec'] // bin_size_sec) * bin_size_sec

    pivot = df_valid.groupby(['time_bin', 'event']).size().unstack(fill_value=0).reset_index()
    return pivot
