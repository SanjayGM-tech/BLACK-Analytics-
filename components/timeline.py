"""
Match Timeline Playback Component
==================================
Allows Level Designers to scrub and replay a match chronologically,
watching player trajectories, fights, loot drops, and storm deaths unfold.
"""

import time
from typing import Tuple
import pandas as pd
import streamlit as st


def format_seconds(seconds: float) -> str:
    """Format seconds into MM:SS display."""
    total_sec = max(0, int(round(seconds)))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"


def render_timeline_controls(match_df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:
    """
    Renders Play/Pause/Reset buttons, speed selector, and match time slider.
    
    Guarantees strict integer types for all Streamlit slider arguments
    to prevent type mismatch exceptions, and safely handles zero-duration
    or single-event matches.
    
    Returns:
        (filtered_df, current_time_sec, max_time_sec)
    """
    if match_df.empty or 'elapsed_sec' not in match_df.columns:
        return match_df, 0, 0

    raw_max = match_df['elapsed_sec'].max()
    if pd.isna(raw_max) or float(raw_max) <= 0:
        st.markdown(
            """
            <div style="background:#0E121B; border:1px solid rgba(255,255,255,0.08); border-radius:6px; padding:8px 12px; margin:8px 0; font-size:12px; color:#8F9CAE;">
                ⏱️ <b>Single Timestamp Session:</b> Match duration is 0 seconds. Full session displayed.
            </div>
            """,
            unsafe_allow_html=True
        )
        return match_df, 0, 0

    max_time_sec = int(max(1, round(float(raw_max))))

    # Match ID tracking to reset playback when switching matches
    active_match_id = str(match_df['match_id'].iloc[0]) if ('match_id' in match_df.columns and not match_df.empty) else ""
    if st.session_state.get("timeline_active_match") != active_match_id:
        st.session_state.timeline_active_match = active_match_id
        st.session_state.playback_time = max_time_sec
        st.session_state.playback_playing = False

    # Initialize playback session state
    if "playback_time" not in st.session_state:
        st.session_state.playback_time = max_time_sec
    if "playback_playing" not in st.session_state:
        st.session_state.playback_playing = False
    if "playback_speed" not in st.session_state:
        st.session_state.playback_speed = 2.0

    # Ensure playback time is clamped within [0, max_time_sec] as integer
    current_time_sec = int(min(max_time_sec, max(0, int(round(st.session_state.playback_time)))))
    st.session_state.playback_time = current_time_sec

    st.markdown(
        """
        <div style="
            background: #0E121B;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 12px 16px;
            margin-top: 10px;
            margin-bottom: 12px;
        ">
            <span style="font-size: 13px; font-weight: 700; color: #00E5FF; letter-spacing: 0.5px;">
                ⏱️ MATCH REPLAY TIMELINE
            </span>
            <span style="font-size: 12px; color: #8F9CAE; margin-left: 10px;">
                Watch player movement and combat unfold dynamically over match duration.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5 = st.columns([1, 1, 1, 1.5, 4.5])

    with ctrl_col1:
        if st.session_state.playback_playing:
            if st.button("⏸️ Pause", use_container_width=True):
                st.session_state.playback_playing = False
                st.rerun()
        else:
            if st.button("▶️ Play", use_container_width=True):
                if st.session_state.playback_time >= max_time_sec:
                    st.session_state.playback_time = 0
                st.session_state.playback_playing = True
                st.rerun()

    with ctrl_col2:
        if st.button("⏹️ Reset", use_container_width=True):
            st.session_state.playback_time = 0
            st.session_state.playback_playing = False
            st.rerun()

    with ctrl_col3:
        if st.button("⏭️ Full", use_container_width=True):
            st.session_state.playback_time = max_time_sec
            st.session_state.playback_playing = False
            st.rerun()

    with ctrl_col4:
        speeds = [1.0, 2.0, 5.0, 10.0]
        curr_speed = float(st.session_state.playback_speed)
        speed_idx = speeds.index(curr_speed) if curr_speed in speeds else 1
        selected_speed = st.selectbox(
            "Playback Speed",
            speeds,
            index=speed_idx,
            format_func=lambda s: f"{int(s)}x Speed",
            label_visibility="collapsed"
        )
        st.session_state.playback_speed = float(selected_speed)

    with ctrl_col5:
        curr_str = format_seconds(current_time_sec)
        max_str = format_seconds(max_time_sec)
        st.markdown(
            f"""
            <div style="text-align: right; font-family: monospace; font-size: 14px; color: #00E5FF; padding-top: 6px;">
                Match Time: <b>{curr_str}</b> / {max_str} ({current_time_sec}s / {max_time_sec}s)
            </div>
            """,
            unsafe_allow_html=True
        )

    # Time Slider - ALL 4 PARAMETERS ARE STRICTLY INT
    slider_step_int = int(max(1, round(max_time_sec / 100)))
    slider_time = st.slider(
        "Match Timeline (Seconds)",
        min_value=0,
        max_value=max_time_sec,
        value=current_time_sec,
        step=slider_step_int,
        label_visibility="collapsed"
    )

    if slider_time != st.session_state.playback_time:
        st.session_state.playback_time = int(slider_time)
        current_time_sec = int(slider_time)

    # Filter telemetry up to the current timestamp
    filtered_df = match_df[match_df['elapsed_sec'] <= current_time_sec].copy()

    # Auto-progression loop when playing
    if st.session_state.playback_playing:
        play_step = max(1, int(round((max_time_sec / 80.0) * float(st.session_state.playback_speed))))
        new_time = current_time_sec + play_step
        if new_time >= max_time_sec:
            st.session_state.playback_time = max_time_sec
            st.session_state.playback_playing = False
        else:
            st.session_state.playback_time = int(new_time)
        time.sleep(0.12)
        st.rerun()

    return filtered_df, current_time_sec, max_time_sec
