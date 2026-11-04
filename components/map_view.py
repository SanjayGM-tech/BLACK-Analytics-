"""
Interactive Minimap View Component for LILA BLACK
==================================================
Renders high-resolution minimap background with overlayed player paths,
combat markers, loot pickups, storm casualties, and spatial heatmaps.
"""

import os
from typing import List, Optional, Dict, Any
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.coordinate_mapper import MAP_CONFIGS
from src.player_paths import create_player_trajectories
from src.event_markers import create_event_markers
from src.heatmaps import create_density_heatmap


def get_minimap_image(map_id: str, assets_dir: str) -> Optional[Image.Image]:
    """Load optimized 1024x1024 minimap, with fallback to raw minimap."""
    opt_file = os.path.join(assets_dir, "minimaps", f"{map_id}_1024.png")
    if os.path.exists(opt_file):
        return Image.open(opt_file)

    config = MAP_CONFIGS.get(map_id, {})
    raw_fname = config.get("minimap_file", "")
    raw_file = os.path.join(assets_dir, "minimaps", raw_fname)
    if os.path.exists(raw_file):
        return Image.open(raw_file)

    return None


def render_interactive_map(
    df: pd.DataFrame,
    map_id: str,
    assets_dir: str,
    heatmap_mode: str = "None",
    heatmap_opacity: float = 0.60,
    heatmap_resolution: int = 40,
    show_trajectories: bool = True,
    show_markers: bool = True,
    selected_users: Optional[List[str]] = None,
    show_humans: bool = True,
    show_bots: bool = True,
    active_events: Optional[List[str]] = None,
    line_width: float = 2.0,
    marker_scale: float = 1.0,
    height: int = 760
) -> go.Figure:
    """
    Construct the full interactive Plotly minimap figure.
    """
    fig = go.Figure()

    # 1. Load and set minimap background image
    minimap_img = get_minimap_image(map_id, assets_dir)
    if minimap_img is not None:
        fig.add_layout_image(
            dict(
                source=minimap_img,
                xref="x",
                yref="y",
                x=0,
                y=0,
                sizex=1024,
                sizey=1024,
                xanchor="left",
                yanchor="top",
                sizing="stretch",
                opacity=1.0,
                layer="below"
            )
        )

    # 2. Add spatial density heatmap if active
    if heatmap_mode and heatmap_mode != "None":
        hm_trace = create_density_heatmap(
            df=df,
            mode=heatmap_mode,
            opacity=heatmap_opacity,
            resolution_bins=heatmap_resolution
        )
        if hm_trace is not None:
            fig.add_trace(hm_trace)

    # 3. Add player movement trajectories
    if show_trajectories and not df.empty:
        trajectory_traces = create_player_trajectories(
            df=df,
            selected_users=selected_users,
            show_humans=show_humans,
            show_bots=show_bots,
            line_width=line_width,
            show_markers=show_markers
        )
        for tr in trajectory_traces:
            fig.add_trace(tr)

    # 4. Add discrete event markers (Kills, Deaths, Loot, Storm Deaths)
    if not df.empty:
        event_traces = create_event_markers(
            df=df,
            active_event_types=active_events,
            marker_scale=marker_scale
        )
        for tr in event_traces:
            fig.add_trace(tr)

    # 5. Configure coordinate axes matching the 1024x1024 top-down projection
    fig.update_xaxes(
        range=[0, 1024],
        showgrid=False,
        zeroline=False,
        visible=False,
        fixedrange=False
    )
    fig.update_yaxes(
        range=[1024, 0],
        autorange="reversed",
        showgrid=False,
        zeroline=False,
        visible=False,
        fixedrange=False,
        scaleanchor="x",
        scaleratio=1
    )

    # 6. Professional Dark Gaming UI Theme
    fig.update_layout(
        height=height,
        margin=dict(l=5, r=5, t=10, b=5),
        template="plotly_dark",
        paper_bgcolor="#0A0D14",
        plot_bgcolor="#0A0D14",
        dragmode="pan",
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(10, 13, 20, 0.85)",
            bordercolor="rgba(255, 255, 255, 0.15)",
            borderwidth=1,
            font=dict(color="#E0E6ED", size=11)
        )
    )

    return fig


def render_map_legend():
    """Render a clean visual key for map elements below the figure."""
    legend_html = """
    <div style="
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;
        justify-content: center;
        background: #0E121B;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 8px 14px;
        margin-top: 6px;
        font-size: 11px;
        color: #A0AEC0;
    ">
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#00E5FF; font-size:14px;">━</span> Human Path</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#FF9100; font-size:14px;">━</span> Bot Path</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#00FF66;">▲</span> Spawn / Start</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#FF0055;">■</span> End / Last Seen</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#FF1744; font-weight:bold;">✚</span> PvP Kill</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#FF5252; font-weight:bold;">✕</span> Bot Kill</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#FFFFFF; font-weight:bold;">⊗</span> PvP Death</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#FF7043; font-weight:bold;">⊕</span> Bot Death</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#00E676;">◆</span> Loot Collected</span>
        <span style="display:flex; align-items:center; gap:5px;"><span style="color:#D500F9;">⬢</span> Storm Death</span>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)
