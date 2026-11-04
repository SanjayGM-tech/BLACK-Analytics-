"""
Data Loading & Processing Architecture for LILA BLACK Telemetry
================================================================
Handles reading Parquet telemetry files, decoding bytes columns,
normalizing timestamps, classifying players/bots, calculating coordinates,
and generating high-performance cached datasets for Streamlit.
"""

import os
import glob
from typing import List, Optional, Tuple, Dict
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd
import numpy as np

from src.coordinate_mapper import add_map_coordinates, MAP_CONFIGS
from src.validators import is_human_user


DATE_FOLDERS = ["February_10", "February_11", "February_12", "February_13", "February_14"]


def decode_event(val) -> str:
    """Decode byte or string event value to utf-8 string."""
    if isinstance(val, (bytes, bytearray)):
        return val.decode('utf-8', errors='ignore')
    return str(val)


def normalize_dataframe(df: pd.DataFrame, compute_coords: bool = True) -> pd.DataFrame:
    """
    Apply standard cleaning, decoding, timestamp correction, and classification.
    """
    if df.empty:
        return df

    df = df.copy()

    # 1. Decode event column
    if 'event' in df.columns:
        if isinstance(df['event'].iloc[0], (bytes, bytearray)):
            df['event'] = df['event'].apply(decode_event)
        df['event'] = df['event'].astype(str)

    # 2. Fix timestamp interpretation
    # Raw parquet column is timestamp[ms], but integer values represent Unix epoch seconds (e.g. 1770754537 = 2026-02-10)
    if 'ts' in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df['ts']):
            if (df['ts'].dt.year < 2000).any():
                # Unit mismatch from parquet: integer was stored as ms instead of seconds
                if df['ts'].dtype == 'datetime64[ns]':
                    raw_sec = df['ts'].astype('int64') // 10**6
                elif df['ts'].dtype == 'datetime64[us]':
                    raw_sec = df['ts'].astype('int64') // 10**3
                else:
                    raw_sec = df['ts'].astype('int64')
                df['ts_sec'] = raw_sec
                df['timestamp'] = pd.to_datetime(df['ts_sec'], unit='s', utc=True)
            else:
                df['timestamp'] = pd.to_datetime(df['ts'], utc=True)
                df['ts_sec'] = df['timestamp'].astype('int64') // 10**9
        elif pd.api.types.is_integer_dtype(df['ts']):
            raw_int = df['ts']
            if (raw_int > 1e11).any():
                ts_sec = raw_int // 1000
            else:
                ts_sec = raw_int
            df['ts_sec'] = ts_sec
            df['timestamp'] = pd.to_datetime(df['ts_sec'], unit='s', utc=True)
        else:
            df['ts_sec'] = pd.to_numeric(df['ts'], errors='coerce').fillna(0).astype('int64')
            df['timestamp'] = pd.to_datetime(df['ts_sec'], unit='s', utc=True)

    # 3. Classify human vs bot
    if 'user_id' in df.columns:
        df['user_id'] = df['user_id'].astype(str)
        df['is_human'] = df['user_id'].apply(is_human_user)
        df['is_bot'] = ~df['is_human']
        df['player_type'] = np.where(df['is_human'], 'Human', 'Bot')

    # 4. Clean match_id string
    if 'match_id' in df.columns:
        df['match_id'] = df['match_id'].astype(str)

    # 5. Add normalized UV and pixel coordinates
    if compute_coords:
        df = add_map_coordinates(df)

    return df


def load_single_file(filepath: str, compute_coords: bool = True) -> pd.DataFrame:
    """Read and normalize a single telemetry file."""
    table = pq.read_table(filepath)
    df = table.to_pandas()
    return normalize_dataframe(df, compute_coords=compute_coords)


def load_match_index(data_dir: str, cache_path: Optional[str] = None) -> pd.DataFrame:
    """
    Construct or load a high-performance index table of all matches.
    Each row contains:
    [match_id, map_id, day, start_time, duration_sec, total_events,
     total_players, human_players, bot_players, total_kills, total_deaths, total_loot, storm_deaths]
    """
    if cache_path and os.path.exists(cache_path):
        return pd.read_parquet(cache_path)

    # Check default processed cache location
    default_cache = os.path.join(data_dir, "..", "data", "processed", "match_index.parquet")
    if os.path.exists(default_cache):
        return pd.read_parquet(default_cache)

    records = []
    for day in DATE_FOLDERS:
        folder = os.path.join(data_dir, day)
        if not os.path.exists(folder):
            continue
        files = glob.glob(os.path.join(folder, "*.nakama-0"))
        for f in files:
            fname = os.path.basename(f)
            clean_name = fname.replace(".nakama-0", "")
            parts = clean_name.split("_")
            user_id = parts[0]
            match_id = parts[1] if len(parts) > 1 else "unknown"
            is_human = is_human_user(user_id)
            
            try:
                t = pq.read_table(f)
                df = t.to_pandas()
            except Exception:
                continue
                
            if df.empty:
                continue
                
            map_id = df['map_id'].iloc[0] if 'map_id' in df.columns else "Unknown"
            
            # Extract raw timestamps in seconds
            if 'ts' in df.columns:
                raw_int = df['ts'].astype('int64')
                if df['ts'].dtype == 'datetime64[ns]':
                    ts_s = raw_int // 10**9
                elif df['ts'].dtype == 'datetime64[us]':
                    ts_s = raw_int // 10**6
                else:
                    ts_s = raw_int // 1000 if (raw_int > 1e11).any() else raw_int
                ts_min = int(ts_s.min())
                ts_max = int(ts_s.max())
            else:
                ts_min = 0
                ts_max = 0
                
            events_raw = df['event'].apply(decode_event) if 'event' in df.columns else pd.Series(dtype=str)
            kills = int(((events_raw == 'BotKill') | (events_raw == 'Kill')).sum())
            deaths = int(((events_raw == 'BotKilled') | (events_raw == 'Killed')).sum())
            storm_deaths = int((events_raw == 'KilledByStorm').sum())
            loot = int((events_raw == 'Loot').sum())
            
            records.append({
                'day': day,
                'match_id': match_id,
                'user_id': user_id,
                'map_id': map_id,
                'is_human': is_human,
                'is_bot': not is_human,
                'ts_min': ts_min,
                'ts_max': ts_max,
                'events_count': len(df),
                'kills': kills,
                'deaths': deaths,
                'storm_deaths': storm_deaths,
                'loot': loot,
                'file_path': f
            })

    if not records:
        return pd.DataFrame()

    df_parts = pd.DataFrame(records)

    # Aggregate by match
    match_grouped = df_parts.groupby(['day', 'map_id', 'match_id']).agg(
        start_ts=('ts_min', 'min'),
        end_ts=('ts_max', 'max'),
        total_files=('user_id', 'count'),
        total_players=('user_id', 'nunique'),
        human_players=('is_human', lambda x: int(x.sum())),
        bot_players=('is_bot', lambda x: int(x.sum())),
        total_events=('events_count', 'sum'),
        total_kills=('kills', 'sum'),
        total_deaths=('deaths', 'sum'),
        total_storm_deaths=('storm_deaths', 'sum'),
        total_loot=('loot', 'sum')
    ).reset_index()

    match_grouped['duration_sec'] = np.maximum(0, match_grouped['end_ts'] - match_grouped['start_ts'])
    match_grouped['start_time'] = pd.to_datetime(match_grouped['start_ts'], unit='s', utc=True)

    # Sort chronologically
    match_grouped = match_grouped.sort_values(by=['start_ts', 'match_id']).reset_index(drop=True)

    # Save to cache if possible
    save_target = cache_path or default_cache
    os.makedirs(os.path.dirname(save_target), exist_ok=True)
    try:
        match_grouped.to_parquet(save_target, index=False)
    except Exception:
        pass

    return match_grouped


def load_match_telemetry(
    match_id: str,
    data_dir: str,
    compute_coords: bool = True
) -> pd.DataFrame:
    """
    Load and concatenate all player/bot trajectories for a specific match.
    Adds `elapsed_sec` from the match start for timeline playback.
    """
    clean_match = match_id.replace('.nakama-0', '')
    pattern = os.path.join(data_dir, "*", f"*_{clean_match}.nakama-0")
    files = glob.glob(pattern)

    if not files:
        # Fallback to search if match_id was the full filename or without suffix
        pattern2 = os.path.join(data_dir, "*", f"*{clean_match}*")
        files = glob.glob(pattern2)

    if not files:
        return pd.DataFrame()

    dfs = []
    for f in files:
        try:
            t = pq.read_table(f)
            df = t.to_pandas()
            dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()

    combined = pd.concat(dfs, ignore_index=True)
    combined = normalize_dataframe(combined, compute_coords=compute_coords)

    # Calculate match-relative elapsed seconds
    if 'ts_sec' in combined.columns and not combined.empty:
        match_start = combined['ts_sec'].min()
        combined['elapsed_sec'] = combined['ts_sec'] - match_start
    else:
        combined['elapsed_sec'] = 0

    # Sort strictly by timestamp and event
    combined = combined.sort_values(by=['ts_sec', 'user_id']).reset_index(drop=True)
    return combined


def load_all_telemetry(
    data_dir: str,
    cache_path: Optional[str] = None,
    force_reload: bool = False
) -> pd.DataFrame:
    """
    Load full multi-day telemetry dataset.
    Uses cached consolidated parquet for sub-second loading after first build.
    """
    default_cache = os.path.join(data_dir, "..", "data", "processed", "telemetry_clean.parquet")
    target = cache_path or default_cache

    if not force_reload and os.path.exists(target):
        return pd.read_parquet(target)

    frames = []
    for day in DATE_FOLDERS:
        folder = os.path.join(data_dir, day)
        if not os.path.exists(folder):
            continue
        files = glob.glob(os.path.join(folder, "*.nakama-0"))
        for f in files:
            try:
                t = pq.read_table(f)
                df = t.to_pandas()
                df['source_day'] = day
                frames.append(df)
            except Exception:
                continue

    if not frames:
        return pd.DataFrame()

    full_df = pd.concat(frames, ignore_index=True)
    full_df = normalize_dataframe(full_df, compute_coords=True)

    # Save to cache
    os.makedirs(os.path.dirname(target), exist_ok=True)
    try:
        full_df.to_parquet(target, index=False)
    except Exception:
        pass

    return full_df
