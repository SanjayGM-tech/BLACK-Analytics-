"""
Discrete Event Markers for LILA BLACK Game Telemetry
=====================================================
Renders specialized, high-contrast visual markers for combat, loot,
and environmental events:
- Kills (Kill, BotKill)
- Deaths (Killed, BotKilled)
- Loot Pickups (Loot)
- Storm Casualties (KilledByStorm)
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.graph_objects as go


EVENT_STYLES = {
    'Kill': {
        'name': 'Player Kill (PvP)',
        'color': '#FF1744',         # Vivid Neon Red
        'symbol': 'cross',
        'size': 12,
        'border_color': '#FFFFFF',
        'border_width': 1.5
    },
    'BotKill': {
        'name': 'Bot Kill',
        'color': '#FF5252',         # Bright Red
        'symbol': 'x',
        'size': 10,
        'border_color': '#000000',
        'border_width': 1.0
    },
    'Killed': {
        'name': 'Player Death (PvP)',
        'color': '#FFFFFF',         # Pure White
        'symbol': 'circle-x',
        'size': 13,
        'border_color': '#D50000',
        'border_width': 2.0
    },
    'BotKilled': {
        'name': 'Death by Bot',
        'color': '#FF7043',         # Deep Coral
        'symbol': 'circle-cross',
        'size': 11,
        'border_color': '#000000',
        'border_width': 1.5
    },
    'KilledByStorm': {
        'name': 'Storm Death',
        'color': '#D500F9',         # Intense Electric Purple
        'symbol': 'hexagon',
        'size': 13,
        'border_color': '#FFFFFF',
        'border_width': 1.8
    },
    'Loot': {
        'name': 'Loot Collected',
        'color': '#00E676',         # Vivid Neon Emerald Green
        'symbol': 'diamond',
        'size': 9,
        'border_color': '#003311',
        'border_width': 1.0
    }
}


def create_event_markers(
    df: pd.DataFrame,
    active_event_types: Optional[List[str]] = None,
    marker_scale: float = 1.0,
    opacity: float = 0.95
) -> List[go.Scatter]:
    """
    Generate Plotly scatter traces for discrete gameplay events.
    
    Args:
        df: Filtered telemetry DataFrame with 'pixel_x', 'pixel_y', 'event', 'user_id', 'match_id'.
        active_event_types: List of event types to render. If None, renders all discrete events.
        marker_scale: Scaling factor for marker size.
        opacity: Opacity for event markers.
        
    Returns:
        List of plotly.graph_objects.Scatter traces, grouped by event type.
    """
    traces = []
    if df.empty or 'event' not in df.columns or 'pixel_x' not in df.columns:
        return traces

    # Filter out movement events to isolate discrete events
    discrete_mask = ~df['event'].isin(['Position', 'BotPosition'])
    events_df = df[discrete_mask].copy()

    if events_df.empty:
        return traces

    if active_event_types is not None:
        events_df = events_df[events_df['event'].isin(active_event_types)]

    if events_df.empty:
        return traces

    # Group by event type so each appears cleanly in the Plotly legend
    for ev_type, style in EVENT_STYLES.items():
        subset = events_df[events_df['event'] == ev_type]
        if subset.empty:
            continue

        hover_text = [
            f"<b>Event:</b> {style['name']}<br>"
            f"<b>Player:</b> {row['user_id']}<br>"
            f"<b>Type:</b> {row.get('player_type', 'Unknown')}<br>"
            f"<b>Match ID:</b> {row['match_id']}<br>"
            f"<b>Match Time:</b> {row.get('elapsed_sec', 0):.1f}s<br>"
            f"<b>World (X, Z):</b> ({row['x']:.1f}, {row['z']:.1f})<br>"
            f"<b>Elevation:</b> {row['y']:.1f}m"
            for _, row in subset.iterrows()
        ]

        trace = go.Scatter(
            x=subset['pixel_x'],
            y=subset['pixel_y'],
            mode='markers',
            marker=dict(
                size=style['size'] * marker_scale,
                color=style['color'],
                symbol=style['symbol'],
                opacity=opacity,
                line=dict(
                    color=style['border_color'],
                    width=style['border_width']
                )
            ),
            hoverinfo='text',
            hovertext=hover_text,
            name=style['name'],
            legendgroup=f"event_{ev_type}",
            showlegend=True
        )
        traces.append(trace)

    return traces
