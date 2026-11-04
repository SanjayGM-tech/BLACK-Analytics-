"""
Validation Utilities for LILA BLACK Telemetry Data
===================================================
Provides schema, coordinate, event, and integrity validation.
"""

from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
from src.coordinate_mapper import MAP_CONFIGS, world_to_uv

REQUIRED_COLUMNS = ['user_id', 'match_id', 'map_id', 'x', 'y', 'z', 'ts', 'event']

VALID_EVENTS = {
    'Position', 'BotPosition', 'Loot',
    'BotKill', 'BotKilled', 'KilledByStorm',
    'Kill', 'Killed'
}


def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Verify that a DataFrame contains all required telemetry columns."""
    errors = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")
    return len(errors) == 0, errors


def validate_events(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Verify that all event types in the DataFrame are recognized."""
    if 'event' not in df.columns or df.empty:
        return True, []
    
    unique_events = set(df['event'].unique())
    unknown = unique_events - VALID_EVENTS
    if unknown:
        return False, [f"Unknown event types encountered: {unknown}"]
    return True, []


def validate_coordinates(
    df: pd.DataFrame,
    margin: float = 0.10
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate that coordinates map into reasonable UV bounds [0 - margin, 1 + margin].
    """
    report = {
        'total_rows': len(df),
        'out_of_bounds_count': 0,
        'nan_coords_count': 0,
        'by_map': {}
    }

    if df.empty or 'x' not in df.columns or 'z' not in df.columns:
        return True, report

    nan_mask = df['x'].isna() | df['z'].isna()
    report['nan_coords_count'] = int(nan_mask.sum())

    for map_id, config in MAP_CONFIGS.items():
        map_df = df[df['map_id'] == map_id]
        if map_df.empty:
            continue
        u, v = world_to_uv(map_df['x'], map_df['z'], map_id)
        oob = (u < -margin) | (u > 1.0 + margin) | (v < -margin) | (v > 1.0 + margin)
        oob_count = int(oob.sum())
        report['out_of_bounds_count'] += oob_count
        report['by_map'][map_id] = {
            'rows': len(map_df),
            'oob_count': oob_count,
            'u_range': (float(u.min()), float(u.max())) if len(u) > 0 else (0.0, 0.0),
            'v_range': (float(v.min()), float(v.max())) if len(v) > 0 else (0.0, 0.0),
        }

    is_valid = (report['out_of_bounds_count'] == 0) and (report['nan_coords_count'] == 0)
    return is_valid, report


def is_human_user(user_id: Any) -> bool:
    """Identify if user_id is a human player (UUID format) or bot (numeric)."""
    s = str(user_id).strip()
    return ('-' in s) and (len(s) >= 32)
