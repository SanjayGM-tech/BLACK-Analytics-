"""
Spatial Heatmap Generation for LILA BLACK Game Telemetry
=========================================================
Implements density overlays for:
- Kill Heatmap (Combat aggression hotspots)
- Death Heatmap (Lethality zones and storm casualties)
- Traffic Heatmap (Movement flow and navigational corridors)
- Loot Heatmap (Item harvesting concentration)
"""

from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import plotly.graph_objects as go


HEATMAP_PRESETS = {
    "Kill": {
        "title": "Kill Density Heatmap",
        "events": ["Kill", "BotKill"],
        "colorscale": "Hot",
        "default_opacity": 0.65,
        "ncontours": 25,
        "description": "Concentration of player and bot eliminations"
    },
    "Death": {
        "title": "Death Density Heatmap",
        "events": ["Killed", "BotKilled", "KilledByStorm"],
        "colorscale": "Magma",
        "default_opacity": 0.65,
        "ncontours": 25,
        "description": "Locations where player deaths occur (including storm casualties)"
    },
    "Traffic": {
        "title": "Player Traffic Density Heatmap",
        "events": ["Position", "BotPosition"],
        "colorscale": "Inferno",
        "default_opacity": 0.55,
        "ncontours": 30,
        "description": "High-traffic navigational routes and player circulation density"
    },
    "Loot": {
        "title": "Loot Collection Heatmap",
        "events": ["Loot"],
        "colorscale": "Viridis",
        "default_opacity": 0.60,
        "ncontours": 25,
        "description": "Frequency of item looting and equipment gathering"
    }
}


def create_density_heatmap(
    df: pd.DataFrame,
    mode: str = "Traffic",
    opacity: Optional[float] = None,
    resolution_bins: int = 40,
    colorscale: Optional[str] = None,
    ncontours: Optional[int] = None,
    show_colorbar: bool = True
) -> Optional[go.Histogram2dContour]:
    """
    Generate a 2D density contour heatmap trace aligned with the 1024x1024 minimap canvas.
    
    Args:
        df: Filtered telemetry DataFrame with 'pixel_x', 'pixel_y', 'event'.
        mode: Heatmap mode ('Kill', 'Death', 'Traffic', 'Loot').
        opacity: Custom opacity (overrides preset default if provided).
        resolution_bins: Number of spatial histogram bins per axis.
        colorscale: Custom Plotly colorscale.
        ncontours: Number of contour density bands.
        show_colorbar: Whether to display the density legend bar.
        
    Returns:
        plotly.graph_objects.Histogram2dContour trace, or None if dataset is empty.
    """
    if df.empty or 'pixel_x' not in df.columns or 'pixel_y' not in df.columns:
        return None

    preset = HEATMAP_PRESETS.get(mode, HEATMAP_PRESETS["Traffic"])
    target_events = preset["events"]

    # Filter for target events
    subset = df[df['event'].isin(target_events)].dropna(subset=['pixel_x', 'pixel_y'])

    if subset.empty:
        return None

    # Enforce minimum points for contouring
    if len(subset) < 2:
        return None

    eff_opacity = opacity if opacity is not None else preset["default_opacity"]
    eff_colorscale = colorscale if colorscale is not None else preset["colorscale"]
    eff_ncontours = ncontours if ncontours is not None else preset["ncontours"]

    trace = go.Histogram2dContour(
        x=subset['pixel_x'],
        y=subset['pixel_y'],
        name=preset["title"],
        colorscale=eff_colorscale,
        opacity=eff_opacity,
        ncontours=eff_ncontours,
        nbinsx=resolution_bins,
        nbinsy=resolution_bins,
        contours=dict(
            coloring='heatmap',
            showlabels=False
        ),
        line=dict(width=0.5, color='rgba(255,255,255,0.15)'),
        hoverinfo='skip',
        showscale=show_colorbar,
        colorbar=dict(
            title=dict(
                text=f"{mode} Density",
                font=dict(color="#FFFFFF", size=11)
            ),
            tickfont=dict(color="#CCCCCC", size=10),
            len=0.6,
            thickness=14,
            x=1.02,
            y=0.5
        )
    )

    return trace


def get_heatmap_stats(df: pd.DataFrame, mode: str = "Traffic") -> Dict[str, Any]:
    """Calculate summary statistics for the selected heatmap mode."""
    preset = HEATMAP_PRESETS.get(mode, HEATMAP_PRESETS["Traffic"])
    subset = df[df['event'].isin(preset["events"])] if not df.empty and 'event' in df.columns else pd.DataFrame()
    
    return {
        "mode": mode,
        "title": preset["title"],
        "description": preset["description"],
        "sample_count": len(subset),
        "unique_players": subset['user_id'].nunique() if 'user_id' in subset.columns else 0,
        "unique_matches": subset['match_id'].nunique() if 'match_id' in subset.columns else 0,
    }
