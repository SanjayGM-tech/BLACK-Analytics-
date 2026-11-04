"""
Sidebar Controls & Filter Component for LILA BLACK Analytics
=============================================================
Manages all user filters, map selections, match exploration,
heatmap toggles, and display preferences.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import streamlit as st

from src.coordinate_mapper import MAP_CONFIGS


def render_sidebar(
    match_index: pd.DataFrame,
    available_users: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Render professional sidebar controls and return a dictionary of active filter states.
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px;">
                <h2 style="margin:0; font-size:18px; color:#00E5FF; font-weight:800; letter-spacing:1px;">
                    🎮 LILA BLACK
                </h2>
                <div style="font-size:11px; color:#8F9CAE; font-weight:600;">
                    LEVEL DESIGNER TELEMETRY SUITE
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 1. Map Selection
        st.markdown("#### 🗺️ Map Selection")
        map_options = list(MAP_CONFIGS.keys())
        selected_map = st.selectbox(
            "Game Map",
            map_options,
            index=0,
            format_func=lambda m: f"{MAP_CONFIGS[m]['name']} ({m})"
        )

        # 2. Date Selection
        st.markdown("#### 📅 Date Filter")
        date_options = ["All Dates", "February_10", "February_11", "February_12", "February_13", "February_14"]
        selected_date = st.selectbox("Date", date_options, index=0)

        # Filter match index for Map & Date to populate Match dropdown
        filtered_index = match_index.copy() if not match_index.empty else pd.DataFrame()
        if not filtered_index.empty:
            filtered_index = filtered_index[filtered_index['map_id'] == selected_map]
            if selected_date != "All Dates":
                filtered_index = filtered_index[filtered_index['day'] == selected_date]

        # 3. Match Mode & Selector
        st.markdown("#### 🎯 Match Exploration")
        match_mode = st.radio(
            "Analysis Scope",
            ["Single Match (Timeline & Detail)", "All Matches (Aggregated Heatmaps)"],
            index=0
        )

        selected_match_id = None
        if match_mode == "Single Match (Timeline & Detail)":
            if not filtered_index.empty:
                # Sort matches by player count descending to surface rich matches first
                sorted_matches = filtered_index.sort_values(
                    by=['total_players', 'total_events'],
                    ascending=[False, False]
                ).reset_index(drop=True)

                match_labels = {}
                for _, r in sorted_matches.iterrows():
                    m_id = r['match_id']
                    short_id = m_id[:8]
                    dur = int(r.get('duration_sec', 0))
                    p_count = int(r.get('total_players', 0))
                    k_count = int(r.get('total_kills', 0))
                    label = f"{short_id}... | {p_count} plyrs | {dur}s | {k_count} kills"
                    match_labels[m_id] = label

                match_keys = list(match_labels.keys())
                chosen_key = st.selectbox(
                    "Select Match",
                    match_keys,
                    format_func=lambda k: match_labels.get(k, k)
                )
                selected_match_id = chosen_key
            else:
                st.warning("No matches available for this map and date.")

        st.markdown("---")

        # 4. Entity & Event Filters
        st.markdown("#### 👥 Player & Event Filters")
        player_type_filter = st.selectbox(
            "Player Type",
            ["All Participants", "Human Players Only", "Bots Only"],
            index=0
        )

        # Individual Player Selector
        selected_players = None
        if available_users and len(available_users) > 0:
            user_options = ["All Players"] + sorted(available_users)
            chosen_user = st.selectbox(
                "Filter Specific Player",
                user_options,
                index=0,
                format_func=lambda u: "All Players" if u == "All Players" else (f"Human: {u[:8]}..." if '-' in u and len(u) > 20 else f"Bot: {u}")
            )
            if chosen_user != "All Players":
                selected_players = [chosen_user]

        discrete_event_options = [
            "Kill", "BotKill", "Killed", "BotKilled", "KilledByStorm", "Loot"
        ]
        active_events = st.multiselect(
            "Active Event Markers",
            discrete_event_options,
            default=discrete_event_options
        )

        st.markdown("---")

        # 5. Spatial Heatmap Mode
        st.markdown("#### 🔥 Spatial Heatmap Overlay")
        heatmap_mode = st.selectbox(
            "Heatmap Mode",
            ["None", "Traffic", "Kill", "Death", "Loot"],
            index=0
        )

        heatmap_opacity = 0.60
        heatmap_resolution = 40
        if heatmap_mode != "None":
            heatmap_opacity = st.slider("Heatmap Opacity", 0.1, 1.0, 0.60, 0.05)
            heatmap_resolution = st.slider("Grid Resolution (Bins)", 20, 80, 40, 5)

        st.markdown("---")

        # 6. Display Preferences
        with st.expander("⚙️ Visual Settings", expanded=False):
            show_trajectories = st.checkbox("Show Trajectory Lines", value=True)
            show_trajectory_dots = st.checkbox("Show Trajectory Point Markers", value=False)
            line_width = st.slider("Trajectory Line Width", 1.0, 5.0, 2.0, 0.5)
            marker_scale = st.slider("Event Marker Size", 0.5, 2.0, 1.0, 0.1)

    return {
        "selected_map": selected_map,
        "selected_date": selected_date,
        "match_mode": match_mode,
        "selected_match_id": selected_match_id,
        "player_type_filter": player_type_filter,
        "selected_players": selected_players,
        "active_events": active_events,
        "heatmap_mode": heatmap_mode,
        "heatmap_opacity": heatmap_opacity,
        "heatmap_resolution": heatmap_resolution,
        "show_trajectories": show_trajectories,
        "show_trajectory_dots": show_trajectory_dots,
        "line_width": line_width,
        "marker_scale": marker_scale,
    }
