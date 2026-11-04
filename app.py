"""
LILA BLACK — Player Journey Visualization Tool
==============================================
Production-grade game analytics application for Level Designers.
Built for LILA Games Product Engineer Assignment.
"""

import os
import sys
import pandas as pd
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.coordinate_mapper import MAP_CONFIGS
from src.data_loader import (
    load_match_index,
    load_match_telemetry,
    load_all_telemetry
)
from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_cards
from components.map_view import render_interactive_map, render_map_legend
from components.timeline import render_timeline_controls
from components.charts import render_analytics_dashboard


# Page configuration
st.set_page_config(
    page_title="LILA BLACK — Player Journey Explorer",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS for Dark Charcoal AAA Gaming UI
st.markdown(
    """
    <style>
        /* Main background and font styling */
        .stApp {
            background-color: #07090E;
            color: #E0E6ED;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0B0E16 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        /* Card and container borders */
        div[data-testid="stExpander"] {
            background-color: #0E121B !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
        }

        /* Button styling */
        .stButton>button {
            background: linear-gradient(180deg, #1A2333, #111722);
            color: #00E5FF;
            border: 1px solid rgba(0, 229, 255, 0.3);
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            border-color: #00E5FF;
            box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
            color: #FFFFFF;
        }

        /* Header styling */
        h1, h2, h3 {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }

        /* Metric cards */
        div[data-testid="metric-container"] {
            background-color: #0E121B;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(show_spinner=False)
def get_cached_match_index(data_dir: str):
    return load_match_index(data_dir)


@st.cache_data(show_spinner=False)
def get_cached_all_telemetry(data_dir: str):
    return load_all_telemetry(data_dir)


@st.cache_data(show_spinner=False)
def get_cached_match_telemetry(match_id: str, data_dir: str):
    return load_match_telemetry(match_id, data_dir)


def main():
    data_dir = os.path.join(PROJECT_ROOT, "player_data")
    assets_dir = os.path.join(PROJECT_ROOT, "assets")

    # Load high-performance match index
    match_index = get_cached_match_index(data_dir)

    # 1. Sidebar Controls
    # Collect available players for the selected match or globally
    active_users = []
    sidebar_params = render_sidebar(match_index=match_index, available_users=active_users)

    selected_map = sidebar_params["selected_map"]
    selected_date = sidebar_params["selected_date"]
    match_mode = sidebar_params["match_mode"]
    selected_match_id = sidebar_params["selected_match_id"]
    player_type_filter = sidebar_params["player_type_filter"]
    selected_players = sidebar_params["selected_players"]
    active_events = sidebar_params["active_events"]
    heatmap_mode = sidebar_params["heatmap_mode"]
    heatmap_opacity = sidebar_params["heatmap_opacity"]
    heatmap_resolution = sidebar_params["heatmap_resolution"]
    show_trajectories = sidebar_params["show_trajectories"]
    show_trajectory_dots = sidebar_params["show_trajectory_dots"]
    line_width = sidebar_params["line_width"]
    marker_scale = sidebar_params["marker_scale"]

    # 2. Header
    map_display_name = MAP_CONFIGS.get(selected_map, {}).get("name", selected_map)
    st.markdown(
        f"""
        <div style="padding: 6px 0 16px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h1 style="margin:0; font-size:26px; font-weight:800; letter-spacing:0.5px;">
                        LILA BLACK <span style="color:#00E5FF;">Analytics</span>
                    </h1>
                    <div style="font-size:13px; color:#8F9CAE; margin-top:2px;">
                        Player Journey Explorer & Spatial Gameplay Intelligence
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:12px; color:#A0AEC0;">
                        Active Map: <b style="color:#00E5FF;">{map_display_name}</b> | Date: <b style="color:#FFFFFF;">{selected_date}</b>
                    </div>
                    <div style="font-size:11px; color:#5A6A80;">
                        Dataset: Feb 10–14, 2026 (89,104 events | 796 matches)
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 3. Load Active Telemetry Dataset
    with st.spinner("Streaming telemetry..."):
        if match_mode == "Single Match (Timeline & Detail)" and selected_match_id:
            raw_telemetry = get_cached_match_telemetry(selected_match_id, data_dir)
        else:
            all_data = get_cached_all_telemetry(data_dir)
            raw_telemetry = all_data[all_data['map_id'] == selected_map].copy() if not all_data.empty else pd.DataFrame()
            if selected_date != "All Dates" and not raw_telemetry.empty:
                raw_telemetry = raw_telemetry[raw_telemetry['source_day'] == selected_date]

    if raw_telemetry.empty:
        st.warning("No telemetry records match your current filter criteria.")
        return

    # Update available users in session if in single match mode
    available_in_scope = raw_telemetry['user_id'].unique().tolist()

    # Apply Player Type filter
    filtered_telemetry = raw_telemetry.copy()
    show_humans = True
    show_bots = True

    if player_type_filter == "Human Players Only":
        filtered_telemetry = filtered_telemetry[filtered_telemetry['is_human']]
        show_bots = False
    elif player_type_filter == "Bots Only":
        filtered_telemetry = filtered_telemetry[filtered_telemetry['is_bot']]
        show_humans = False

    # Apply Individual Player Filter
    if selected_players:
        filtered_telemetry = filtered_telemetry[filtered_telemetry['user_id'].isin(selected_players)]

    # 4. Section A: KPI Cards (Calculated directly from filtered telemetry)
    total_matches = int(filtered_telemetry['match_id'].nunique())
    total_players = int(filtered_telemetry['user_id'].nunique())
    human_players = int(filtered_telemetry[filtered_telemetry['is_human']]['user_id'].nunique())
    bot_players = int(filtered_telemetry[filtered_telemetry['is_bot']]['user_id'].nunique())
    total_kills = int(((filtered_telemetry['event'] == 'Kill') | (filtered_telemetry['event'] == 'BotKill')).sum())
    total_deaths = int(((filtered_telemetry['event'] == 'Killed') | (filtered_telemetry['event'] == 'BotKilled')).sum())
    total_loot = int((filtered_telemetry['event'] == 'Loot').sum())
    storm_deaths = int((filtered_telemetry['event'] == 'KilledByStorm').sum())

    kpi_metrics = {
        'total_matches': total_matches,
        'total_players': total_players,
        'human_players': human_players,
        'bot_players': bot_players,
        'total_kills': total_kills,
        'total_deaths': total_deaths,
        'total_loot': total_loot,
        'storm_deaths': storm_deaths
    }
    render_kpi_cards(kpi_metrics)

    # 5. Section D: Match Timeline Playback (Active when in Single Match Mode)
    map_telemetry = filtered_telemetry
    if match_mode == "Single Match (Timeline & Detail)" and selected_match_id:
        map_telemetry, curr_time, max_time = render_timeline_controls(filtered_telemetry)

    # 6. Section B & C: Interactive Minimap & Heatmap
    st.markdown("")
    map_fig = render_interactive_map(
        df=map_telemetry,
        map_id=selected_map,
        assets_dir=assets_dir,
        heatmap_mode=heatmap_mode,
        heatmap_opacity=heatmap_opacity,
        heatmap_resolution=heatmap_resolution,
        show_trajectories=show_trajectories,
        show_markers=show_trajectory_dots,
        selected_users=selected_players,
        show_humans=show_humans,
        show_bots=show_bots,
        active_events=active_events,
        line_width=line_width,
        marker_scale=marker_scale
    )
    st.plotly_chart(map_fig, use_container_width=True)
    render_map_legend()

    # 7. Section E: Analytics Visualizations
    st.markdown("---")
    render_analytics_dashboard(filtered_telemetry, match_index)


if __name__ == "__main__":
    main()
