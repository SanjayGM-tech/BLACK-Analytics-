"""
Level Design Analytics Charts Component
========================================
Visualizations helping Level Designers evaluate map flow, kill hotspots,
chokepoints, human vs bot engagement, and pacing.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    compute_quadrant_distribution,
    compute_human_bot_summary,
    compute_temporal_event_distribution
)


CHART_THEME = {
    'paper_bgcolor': 'rgba(14, 18, 27, 0.95)',
    'plot_bgcolor': 'rgba(14, 18, 27, 0.95)',
    'font': {'color': '#E0E6ED', 'size': 11},
    'margin': dict(l=25, r=20, t=35, b=25)
}


def render_analytics_dashboard(df: pd.DataFrame, match_index_df: pd.DataFrame):
    """Render Section E: Analytics charts."""
    st.markdown("### 📊 Level Design Analytics & Spatial Intelligence")

    if df.empty:
        st.info("No telemetry records available for the active filter selection.")
        return

    row1_col1, row1_col2 = st.columns(2)

    # 1. Spatial Combat Hotspots by Quadrant
    with row1_col1:
        kill_quad = compute_quadrant_distribution(df, ['Kill', 'BotKill'])
        death_quad = compute_quadrant_distribution(df, ['Killed', 'BotKilled', 'KilledByStorm'])

        fig_quad = go.Figure()
        fig_quad.add_trace(go.Bar(
            name='Kills',
            x=kill_quad['Quadrant'],
            y=kill_quad['Count'],
            marker_color='#FF1744'
        ))
        fig_quad.add_trace(go.Bar(
            name='Deaths',
            x=death_quad['Quadrant'],
            y=death_quad['Count'],
            marker_color='#9D00FF'
        ))
        fig_quad.update_layout(
            title=dict(text="Combat Engagements by Map Quadrant", font=dict(size=13, color="#00E5FF")),
            barmode='group',
            height=320,
            **CHART_THEME
        )
        st.plotly_chart(fig_quad, use_container_width=True)

    # 2. Human vs. Bot Entity Engagement Comparison
    with row1_col2:
        hb = compute_human_bot_summary(df)
        labels = ['Human Kills', 'Bot Kills on Humans', 'Human Deaths to Storm']
        values = [hb['human_kills'], hb['bot_kills'], int((df['event'] == 'KilledByStorm').sum())]
        colors = ['#00E5FF', '#FF9100', '#D500F9']

        fig_hb = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.45,
            marker=dict(colors=colors),
            textinfo='label+percent'
        )])
        fig_hb.update_layout(
            title=dict(text="Lethality Breakdown (Humans vs. Bots vs. Storm)", font=dict(size=13, color="#00E5FF")),
            height=320,
            showlegend=False,
            **CHART_THEME
        )
        st.plotly_chart(fig_hb, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)

    # 3. Events Over Time (Pacing Curve)
    with row2_col1:
        temporal = compute_temporal_event_distribution(df, bin_size_sec=15)
        if not temporal.empty and 'time_bin' in temporal.columns:
            fig_time = go.Figure()
            event_colors = {
                'Position': '#42A5F5',
                'BotPosition': '#FFA726',
                'Loot': '#00E676',
                'BotKill': '#FF1744',
                'BotKilled': '#FF7043',
                'KilledByStorm': '#D500F9',
                'Kill': '#FF1744',
                'Killed': '#FFFFFF'
            }
            # Plot discrete events excluding pure positions for clarity
            for ev in ['Loot', 'BotKill', 'BotKilled', 'KilledByStorm', 'Kill']:
                if ev in temporal.columns:
                    fig_time.add_trace(go.Scatter(
                        x=temporal['time_bin'],
                        y=temporal[ev],
                        mode='lines+markers',
                        name=ev,
                        line=dict(color=event_colors.get(ev, '#CCCCCC'), width=2),
                        marker=dict(size=5)
                    ))
            fig_time.update_layout(
                title=dict(text="Event Intensity Across Match Timeline (Pacing)", font=dict(size=13, color="#00E5FF")),
                xaxis_title="Match Elapsed Seconds",
                yaxis_title="Event Frequency",
                height=320,
                **CHART_THEME
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            # Fallback event frequency bar chart
            ev_counts = df['event'].value_counts().reset_index()
            ev_counts.columns = ['Event', 'Count']
            fig_ev = px.bar(
                ev_counts,
                x='Event',
                y='Count',
                color='Event',
                title="Telemetry Event Volume"
            )
            fig_ev.update_layout(height=320, showlegend=False, **CHART_THEME)
            st.plotly_chart(fig_ev, use_container_width=True)

    # 4. Match Duration Distribution (from Match Index)
    with row2_col2:
        if not match_index_df.empty and 'duration_sec' in match_index_df.columns:
            fig_dur = px.histogram(
                match_index_df[match_index_df['duration_sec'] > 0],
                x='duration_sec',
                nbins=30,
                title="Match Duration Distribution (All Matches)",
                color_discrete_sequence=['#00E5FF']
            )
            fig_dur.update_layout(
                xaxis_title="Duration (Seconds)",
                yaxis_title="Match Count",
                height=320,
                **CHART_THEME
            )
            st.plotly_chart(fig_dur, use_container_width=True)
        else:
            st.write("Duration data unavailable.")
