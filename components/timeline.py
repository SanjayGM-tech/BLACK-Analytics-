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
    total_sec = max(0, int(seconds))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"


def render_timeline_controls(match_df: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
    """
    Renders Play/Pause/Reset buttons, speed selector, and match time slider.
    Returns:
        (filtered_df, current_time, max_time)
    """
    if match_df.empty or 'elapsed_sec' not in match_df.columns:
        return match_df, 0.0, 0.0

    max_time = float(match_df['elapsed_sec'].max())
    if max_time <= 0:
        return match_df, 0.0, 0.0

    # Initialize playback state in session_state
    if "playback_time" not in st.session_state:
        st.session_state.playback_time = max_time
    if "playback_playing" not in st.session_state:
        st.session_state.playback_playing = False
    if "playback_speed" not in st.session_state:
        st.session_state.playback_speed = 2.0

    # Ensure playback time does not exceed current match duration
    if st.session_state.playback_time > max_time:
        st.session_state.playback_time = max_time

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
                # If already at the end, restart from 0
                if st.session_state.playback_time >= max_time:
                    st.session_state.playback_time = 0.0
                st.session_state.playback_playing = True
                st.rerun()

    with ctrl_col2:
        if st.button("⏹️ Reset", use_container_width=True):
            st.session_state.playback_time = 0.0
            st.session_state.playback_playing = False
            st.rerun()

    with ctrl_col3:
        if st.button("⏭️ Full", use_container_width=True):
            st.session_state.playback_time = max_time
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
        st.session_state.playback_speed = selected_speed

    with ctrl_col5:
        # Time display badge
        curr_str = format_seconds(st.session_state.playback_time)
        max_str = format_seconds(max_time)
        st.markdown(
            f"""
            <div style="text-align: right; font-family: monospace; font-size: 14px; color: #00E5FF; padding-top: 6px;">
                Match Time: <b>{curr_str}</b> / {max_str} ({st.session_state.playback_time:.0f}s / {max_time:.0f}s)
            </div>
            """,
            unsafe_allow_html=True
        )

    # Time Slider
    slider_time = st.slider(
        "Match Timeline (Seconds)",
        min_value=0.0,
        max_value=max_time,
        value=float(st.session_state.playback_time),
        step=max(1.0, round(max_time / 100)),
        label_visibility="collapsed"
    )

    # Update state from slider if user interacted
    if slider_time != st.session_state.playback_time:
        st.session_state.playback_time = slider_time

    # Filter telemetry up to the current timestamp
    filtered_df = match_df[match_df['elapsed_sec'] <= st.session_state.playback_time].copy()

    # Handle auto-progression loop if playing
    if st.session_state.playback_playing:
        step = max(2.0, (max_time / 80.0) * st.session_state.playback_speed)
        new_time = st.session_state.playback_time + step
        if new_time >= max_time:
            st.session_state.playback_time = max_time
            st.session_state.playback_playing = False
        else:
            st.session_state.playback_time = new_time
        time.sleep(0.12)
        st.rerun()

    return filtered_df, st.session_state.playback_time, max_time
