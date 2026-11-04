"""
Player Trajectory Visualization Module for LILA BLACK
======================================================
Builds chronological movement paths, distinguishing human players (Cyan)
from bots (Orange), handling multi-player filtering, and preventing
cross-match or cross-player line interpolation.
"""

from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go


HUMAN_COLOR = "#00E5FF"       # Electric Cyan
BOT_COLOR = "#FF9100"         # Vibrant Orange
START_COLOR = "#00FF66"       # Bright Green for trajectory start
END_COLOR = "#FF0055"         # Bright Magenta/Red for trajectory end


def create_player_trajectories(
    df: pd.DataFrame,
    selected_users: Optional[List[str]] = None,
    show_humans: bool = True,
    show_bots: bool = True,
    line_width: float = 2.0,
    opacity: float = 0.85,
    show_markers: bool = True
) -> List[go.Scatter]:
    """
    Generate Plotly scatter traces for player trajectories.
    Each player's path is drawn strictly chronologically within their match.
    
    Args:
        df: Filtered telemetry DataFrame with 'pixel_x', 'pixel_y', 'ts_sec', 'user_id', 'is_human'.
        selected_users: Optional subset of user_ids to display. If None or empty, shows all.
        show_humans: Whether to render human paths.
        show_bots: Whether to render bot paths.
        line_width: Width of the path lines.
        opacity: Transparency of trajectory lines.
        show_markers: Whether to show small positional dots along the path.
        
    Returns:
        List of plotly.graph_objects.Scatter traces.
    """
    traces = []
    if df.empty or 'pixel_x' not in df.columns or 'pixel_y' not in df.columns:
        return traces

    # Filter movement events ('Position' and 'BotPosition')
    movement_mask = df['event'].isin(['Position', 'BotPosition'])
    pos_df = df[movement_mask].copy()

    if pos_df.empty:
        return traces

    # Drop any null or invalid coordinates
    pos_df = pos_df.dropna(subset=['pixel_x', 'pixel_y', 'ts_sec'])

    # Filter by user selection
    if selected_users:
        pos_df = pos_df[pos_df['user_id'].isin(selected_users)]

    # Filter by player type
    if not show_humans:
        pos_df = pos_df[pos_df['is_bot']]
    if not show_bots:
        pos_df = pos_df[pos_df['is_human']]

    if pos_df.empty:
        return traces

    # Group strictly by (match_id, user_id) to NEVER connect different players or matches
    grouped = pos_df.groupby(['match_id', 'user_id'], sort=False)

    for (match_id, user_id), group in grouped:
        if len(group) < 1:
            continue

        # Sort strictly chronologically
        sorted_group = group.sort_values(by='ts_sec').reset_index(drop=True)
        
        is_human = sorted_group['is_human'].iloc[0]
        color = HUMAN_COLOR if is_human else BOT_COLOR
        player_type = "Human" if is_human else "Bot"
        short_id = user_id[:8] if is_human else f"Bot-{user_id}"

        # Hover text details
        hover_text = [
            f"<b>{player_type}:</b> {user_id}<br>"
            f"<b>Match:</b> {match_id[:8]}...<br>"
            f"<b>Event:</b> {row['event']}<br>"
            f"<b>Match Time:</b> {row.get('elapsed_sec', 0):.1f}s<br>"
            f"<b>World (X, Z):</b> ({row['x']:.1f}, {row['z']:.1f})<br>"
            f"<b>Elevation (Y):</b> {row['y']:.1f}m"
            for _, row in sorted_group.iterrows()
        ]

        # 1. Trajectory line trace
        mode = "lines+markers" if show_markers else "lines"
        line_trace = go.Scatter(
            x=sorted_group['pixel_x'],
            y=sorted_group['pixel_y'],
            mode=mode,
            line=dict(color=color, width=line_width),
            marker=dict(size=4, color=color, opacity=0.7) if show_markers else None,
            opacity=opacity,
            hoverinfo="text",
            hovertext=hover_text,
            name=f"{player_type}: {short_id}",
            legendgroup=f"player_{user_id}",
            showlegend=False
        )
        traces.append(line_trace)

        # 2. Start landmark marker (Spawn / Path Origin)
        start_row = sorted_group.iloc[0]
        start_marker = go.Scatter(
            x=[start_row['pixel_x']],
            y=[start_row['pixel_y']],
            mode="markers",
            marker=dict(
                size=8,
                color=START_COLOR,
                symbol="triangle-up",
                line=dict(color="#000000", width=1.5)
            ),
            hoverinfo="text",
            hovertext=[f"<b>Start Location:</b> {player_type} {short_id}<br>World: ({start_row['x']:.1f}, {start_row['z']:.1f})"],
            legendgroup=f"player_{user_id}",
            showlegend=False
        )
        traces.append(start_marker)

        # 3. End landmark marker (Last seen position / Extraction or Death)
        if len(sorted_group) > 1:
            end_row = sorted_group.iloc[-1]
            end_marker = go.Scatter(
                x=[end_row['pixel_x']],
                y=[end_row['pixel_y']],
                mode="markers",
                marker=dict(
                    size=8,
                    color=END_COLOR,
                    symbol="square",
                    line=dict(color="#000000", width=1.5)
                ),
                hoverinfo="text",
                hovertext=[f"<b>Final Location:</b> {player_type} {short_id}<br>World: ({end_row['x']:.1f}, {end_row['z']:.1f})"],
                legendgroup=f"player_{user_id}",
                showlegend=False
            )
            traces.append(end_marker)

    return traces
