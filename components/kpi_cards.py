"""
KPI Summary Cards Component
============================
Displays high-level operational metrics for the filtered telemetry subset.
"""

from typing import Dict, Any
import streamlit as st


def render_kpi_cards(metrics: Dict[str, Any]):
    """
    Render 8 polished gaming analytics metric cards.
    """
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    cards = [
        {"col": col1, "label": "MATCHES", "val": f"{metrics.get('total_matches', 0):,}", "color": "#00E5FF", "icon": "🎮"},
        {"col": col2, "label": "TOTAL PLAYERS", "val": f"{metrics.get('total_players', 0):,}", "color": "#E0E0E0", "icon": "👥"},
        {"col": col3, "label": "HUMANS", "val": f"{metrics.get('human_players', 0):,}", "color": "#00E5FF", "icon": "🧑"},
        {"col": col4, "label": "BOTS", "val": f"{metrics.get('bot_players', 0):,}", "color": "#FF9100", "icon": "🤖"},
        {"col": col5, "label": "TOTAL KILLS", "val": f"{metrics.get('total_kills', 0):,}", "color": "#FF1744", "icon": "⚔️"},
        {"col": col6, "label": "TOTAL DEATHS", "val": f"{metrics.get('total_deaths', 0):,}", "color": "#FF5252", "icon": "💀"},
        {"col": col7, "label": "LOOT EVENTS", "val": f"{metrics.get('total_loot', 0):,}", "color": "#00E676", "icon": "💎"},
        {"col": col8, "label": "STORM DEATHS", "val": f"{metrics.get('storm_deaths', 0):,}", "color": "#D500F9", "icon": "🌪️"},
    ]

    for item in cards:
        with item["col"]:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(20, 24, 33, 0.95), rgba(13, 16, 23, 0.95));
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-top: 3px solid {item['color']};
                    border-radius: 8px;
                    padding: 10px 8px;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
                    min-height: 85px;
                ">
                    <div style="font-size: 10px; font-weight: 700; letter-spacing: 0.8px; color: #8F9CAE; margin-bottom: 4px;">
                        {item['icon']} {item['label']}
                    </div>
                    <div style="font-size: 20px; font-weight: 800; color: {item['color']}; font-family: 'Segoe UI', monospace;">
                        {item['val']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
