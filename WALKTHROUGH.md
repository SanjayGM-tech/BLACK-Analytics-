# Product Walkthrough & Demonstration Guide

**Project:** Player Journey Visualization Tool — LILA Games  
**User Persona:** Game Level Designer / Analytics Engineer  

This guide provides a comprehensive 10-step demonstration script for evaluating the capabilities of the Player Journey Explorer.

---

## Step 1: Launching the Dashboard

1. Launch the application in your terminal:
   ```bash
   streamlit run app.py
   ```
2. The browser opens to the dark-themed AAA gaming interface.
3. Observe the **Header Section**:
   - Title: **LILA BLACK Analytics — Player Journey Explorer**.
   - Active Map and Date Indicators.
   - Dataset metadata: 89,104 events across 796 matches.

---

## Step 2: Exploring the Three Game Maps

1. Navigate to the left sidebar under **🗺️ Map Selection**.
2. Select **Ambrose Valley**:
   - The map background loads the high-resolution top-down valley map.
   - Coordinate origin $(-370, -473)$ and scale $900$ align telemetry accurately with visual terrain features.
3. Switch to **Grand Rift**:
   - Minimap switches to the canyon landscape ($S=581, O=(-290, -290)$).
   - Notice the central canyon bridge and tactical choke points.
4. Switch to **Lockdown**:
   - Minimap switches to the urban, interior-heavy military complex ($S=1000, O=(-500, -500)$).

---

## Step 3: Selecting and Inspecting a Specific Match

1. In the sidebar under **Analysis Scope**, ensure **Single Match (Timeline & Detail)** is selected.
2. Select **Ambrose Valley**.
3. In the **Select Match** dropdown, choose the top match:
   `fbbc5d02... | 16 plyrs | 622s | 17 kills`
4. Notice how the **Section A: KPI Cards** immediately update:
   - Total Matches: 1
   - Total Players: 16 (1 Human, 15 Bots)
   - Total Kills: 17
   - Total Deaths: 1
   - Total Loot Events: 34
   - Storm Deaths: 0

---

## Step 4: Viewing Player Trajectories

1. Look at the interactive minimap in **Section B**:
   - Continuous line traces appear across the terrain.
   - Green triangles (`▲`) mark the initial spawn/insertion points for participants.
   - Red squares (`■`) mark the final recorded positions where players either extracted or died.
2. Hover over any point along the trajectory line:
   - Tooltip reveals: Player Type, Player ID, Match Time in seconds, World $(X, Z)$ coordinates, and vertical Elevation $(Y)$ in meters.

---

## Step 5: Comparing Human Players and Bots

1. Observe the trajectory color palette:
   - **Electric Cyan (`#00E5FF`):** Represents human player paths.
   - **Vibrant Orange (`#FF9100`):** Represents AI bot patrol paths.
2. In the sidebar under **Player & Event Filters**, select **"Human Players Only"**:
   - All orange bot traces disappear, isolating the single human's tactical navigation.
3. Change filter to **"Bots Only"**:
   - Bot patrol circuits and perimeter loops become clearly visible.
4. Reset to **"All Participants"** to see combined interaction.

---

## Step 6: Inspecting Combat, Loot, and Storm Casualties

1. Review the discrete event markers on the minimap:
   - **Neon Red Cross (`✕`):** Bot kills executed by the human player.
   - **Coral Circle-Cross (`⊕`):** Location where the player took damage or was eliminated by bots.
   - **Emerald Green Diamond (`◆`):** Loot chests and weapon crate pickups.
   - **Electric Purple Hexagon (`⬢`):** Environmental casualties where players were consumed by the storm safe-zone collapse.
2. In the sidebar, toggle the **Active Event Markers** multiselect to isolate specific event categories (e.g. uncheck Loot to focus exclusively on combat engagements).

---

## Step 7: Running the Dynamic Match Timeline Replay

1. Locate **Section D: Match Replay Timeline** directly above the map:
   - Current Match Time badge displays formatted match time: `00:00 / 10:22`.
2. Click **▶️ Play**:
   - The timeline begins auto-advancing at the selected speed (e.g. 2x).
   - Player trajectories progressively draw themselves forward across the terrain.
   - Combat markers and loot pickups appear at the exact moment they occurred in match time.
3. Click **⏸️ Pause** to freeze the match at a critical firefight.
4. Drag the **Time Slider** manually to scrub forward or backward to inspect player positioning prior to an elimination.
5. Click **⏹️ Reset** to return to $0\text{s}$, or **⏭️ Full** to display the entire completed journey.

---

## Step 8: Switching Spatial Heatmap Modes

1. In the sidebar, navigate to **🔥 Spatial Heatmap Overlay**.
2. Select **Traffic Heatmap**:
   - An intense `Inferno` density contour overlays the map, revealing the primary navigational arteries and traversal corridors.
3. Switch to **Kill Heatmap**:
   - A high-contrast `Hot` red density contour highlights primary combat engagement hotspots.
4. Switch to **Death Heatmap**:
   - Highlights player lethality zones and storm perimeter casualties.
5. Adjust the **Heatmap Opacity** slider to balance heatmap visibility against map terrain features.
6. Adjust the **Grid Resolution (Bins)** slider to toggle between broad regional heat and sharp localized clusters.

---

## Step 9: Macro Level Analytics Across All Matches

1. In the sidebar under **Analysis Scope**, switch to **"All Matches (Aggregated Heatmaps)"**.
2. Select **All Dates** and map **Ambrose Valley**:
   - Section A updates to show aggregate numbers across all 566 matches: 61,013 events, 201 human players, 94 bots, 1,799 kills, 505 deaths, 9,955 loot events.
3. Scroll down to **Section E: Level Design Analytics**:
   - **Quadrant Distribution:** Observe the massive skew showing Northwest (34.0%) and Southwest (39.3%) dominating Northeast (9.8%).
   - **Lethality Breakdown:** Visual breakdown of Human Kills vs Bot Kills on Humans vs Storm Deaths.
   - **Pacing Curve:** Event intensity over elapsed match time, displaying initial looting spikes followed by mid-match combat peaks.
   - **Match Duration Histogram:** Distribution showing the modal match length between 5 and 10 minutes.

---

## Step 10: Reviewing the Three Game Insights

Review the three documented design insights in `INSIGHTS.md`:
1. **Insight 1 (Ambrose Valley Western Skew):** 73.3% of all telemetry is locked in the western flank, leaving the Northeast quadrant (9.8%) almost completely unvisited.
   - *Design Action:* Place high-tier weapon caches and dynamic extraction landing zones in the Northeast.
2. **Insight 2 (Lockdown Storm Chokepoints):** Lockdown and Grand Rift have a ~9.2–9.6% storm death rate (nearly triple Ambrose Valley's 3.4%) concentrated in central interior bottlenecks.
   - *Design Action:* Increase warning lead-time by 15s and widen central interior doors.
3. **Insight 3 (99.88% PvE Combat Saturation):** In 796 matches, only 3 human-on-human kills occurred; players are effectively playing solo PvE against 15 bots.
   - *Design Action:* Introduce central High-Value Target (HVT) beacons that force human convergence before extraction.
