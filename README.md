# Player Journey Visualization Tool — LILA Games

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive, browser-based telemetry visualization suite built for **LILA Games Level Designers** to analyze player navigation, combat engagements, storm mortality, and loot economy in **LILA BLACK** (an extraction shooter).

---

## 🌟 Key Features

- **🗺️ High-Fidelity Minimap Projection:** Accurate world-to-minimap coordinate mapping for all three game maps: **Ambrose Valley**, **Grand Rift**, and **Lockdown**.
- **🧑🤖 Human vs. Bot Differentiation:** Clear color-coded trajectory paths (Electric Cyan for Humans, Vibrant Orange for Bots) with spawn and final location markers.
- **⚔️ Complete Combat & Event Overlay:** Distinct high-contrast visual markers for PvP Kills, Bot Kills, PvP Deaths, Bot Deaths, Loot Pickups, and Storm Casualties (`KilledByStorm`).
- **⏱️ Dynamic Match Timeline Playback:** Scrub, play, pause, reset, and adjust playback speed (1x to 10x) to watch matches unfold dynamically over time.
- **🔥 Multi-Mode Spatial Density Heatmaps:** Switch seamlessly between **Traffic Density**, **Kill Hotspots**, **Death Hotspots**, and **Loot Collection** with real-time intensity and resolution controls.
- **📊 Level Design Analytics:** Quadrant spatial breakdown (NW, NE, SW, SE), lethality breakdowns, match pacing curves, and match duration distributions.
- **⚡ Sub-Second Performance:** Snappy caching layer (`pyarrow` / Parquet) loads 89,104 telemetry events in under 100 milliseconds.

---

## 🛠️ Technology Stack

- **Backend & Data Processing:** Python 3.10+, Pandas, PyArrow, NumPy
- **Frontend Framework:** Streamlit
- **Spatial Visualization:** Plotly Graph Objects (WebGL & SVG)
- **Image Processing:** Pillow (PIL) Lanczos resampling
- **Testing & Quality Assurance:** Pytest

---

## 📂 Repository Structure

```
lila-player-journey/
│
├── app.py                     # Streamlit application entry point
├── requirements.txt           # Project dependencies
├── conftest.py                # Pytest path configuration
├── README.md                  # Project overview & instructions
├── ARCHITECTURE.md            # Technical architecture & formulas
├── INSIGHTS.md                # 3 evidence-backed level design insights
├── DATA_DICTIONARY.md         # Schema & telemetry specification
├── WALKTHROUGH.md             # Demonstration script & review guide
├── .gitignore                 # Git ignore rules
│
├── src/                       # Core engine & algorithms
│   ├── __init__.py
│   ├── coordinate_mapper.py   # World-to-minimap math transformation
│   ├── data_loader.py         # Parquet ingestion, decoding & caching
│   ├── player_paths.py        # Chronological trajectories & styling
│   ├── event_markers.py       # Combat, loot & storm markers
│   ├── heatmaps.py            # Spatial 2D density contour generation
│   ├── analytics.py           # Statistical aggregation algorithms
│   └── validators.py          # Schema & coordinate boundary validation
│
├── components/                # UI presentation layer
│   ├── __init__.py
│   ├── sidebar.py             # Map, date, match, entity & event filters
│   ├── kpi_cards.py           # Section A: 8 gaming metric cards
│   ├── map_view.py            # Section B: Minimap canvas & legend
│   ├── timeline.py            # Section D: Play/pause replay controller
│   └── charts.py              # Section E: Spatial & pacing analytics
│
├── assets/
│   └── minimaps/              # Map images (AmbroseValley, GrandRift, Lockdown)
│
├── data/
│   ├── README.md              # Dataset structure & placement guide
│   └── processed/             # Precomputed clean parquet & match index
│
├── tests/
│   ├── test_coordinate_mapper.py
│   ├── test_data_loader.py
│   ├── test_player_paths.py
│   └── test_event_markers.py
│
└── .streamlit/
    └── config.toml            # Dark charcoal gaming UI theme
```

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- Python 3.10 or higher installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/lila-player-journey.git
cd lila-player-journey
```

### 3. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Dataset Placement
Extract `player_data.zip` so that the `player_data/` folder resides in the root directory:
```
player_data/
├── February_10/
├── February_11/
├── February_12/
├── February_13/
├── February_14/
├── minimaps/
└── README.md
```
*Note: The application automatically scans and generates high-performance caches on the first launch.*

### 6. Run the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite covering coordinate mapping, parquet decoding, timestamp reconstruction, human/bot classification, and event rendering:

```bash
pytest tests/ -v
```

All 19 tests will pass with detailed verification output:
```
tests/test_coordinate_mapper.py::test_readme_ambrose_valley_example PASSED
tests/test_coordinate_mapper.py::test_grand_rift_boundaries PASSED
tests/test_coordinate_mapper.py::test_lockdown_center_and_bounds PASSED
tests/test_coordinate_mapper.py::test_inverse_mapping_roundtrip PASSED
tests/test_coordinate_mapper.py::test_add_map_coordinates_dataframe PASSED
tests/test_coordinate_mapper.py::test_boundary_checks PASSED
tests/test_coordinate_mapper.py::test_invalid_map_raises_error PASSED
tests/test_data_loader.py::test_decode_event PASSED
tests/test_data_loader.py::test_human_bot_classification PASSED
tests/test_data_loader.py::test_normalize_dataframe PASSED
tests/test_data_loader.py::test_load_real_sample_file PASSED
tests/test_data_loader.py::test_load_match_telemetry_elapsed_time PASSED
tests/test_event_markers.py::test_empty_dataframe_returns_empty_markers PASSED
tests/test_event_markers.py::test_filters_out_positional_events PASSED
tests/test_event_markers.py::test_renders_discrete_event_categories PASSED
tests/test_event_markers.py::test_selective_event_filtering PASSED
tests/test_player_paths.py::test_empty_dataframe_returns_empty_traces PASSED
tests/test_player_paths.py::test_trajectory_separation_and_styling PASSED
tests/test_player_paths.py::test_chronological_ordering PASSED
```

---

## ☁️ Deployment to Streamlit Community Cloud

The repository is pre-configured for one-click deployment on Streamlit Community Cloud:

1. Push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Click **"New app"**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. Click **"Deploy"**.

**Live Deployment URL:**  
*(Placeholder: Ready for Streamlit Community Cloud deployment)*  
`https://lila-player-journey.streamlit.app`

---

## 🔍 Game Design Insights Preview

Read the complete analysis with supporting evidence and recommendations in [INSIGHTS.md](file:///c:/Users/Sanjay%20gm/Downloads/LILA%20GAMES/INSIGHTS.md):

1. **Severe Western Congestion vs. Northeast Map Desertion:** 73.3% of all telemetry in Ambrose Valley occurs in the western half, while the Northeast quadrant receives only 9.8% of player traffic.
2. **Lockdown & Grand Rift Storm Bottlenecks:** Chokepoints cause nearly 3× higher storm death rates in Lockdown (9.19%) and Grand Rift (9.62%) compared to Ambrose Valley (3.37%).
3. **99.88% PvE Combat Saturation:** Matches average 1.14 humans to 13.8 bots; only 3 human-on-human PvP kills occurred in 5 days of production matches.

---

## ⚠️ Known Nuances & Dataset Limitations

- **Parquet Timestamp Encoding:** The raw parquet column metadata was marked `timestamp[ms]`, but stored Unix epoch seconds (e.g. `1770754537`). The data loader automatically corrects this to true February 2026 UTC timestamps.
- **2D Planar Projection:** The telemetry includes 3D coordinates $(x, y, z)$, where $y$ represents elevation. $y$ is exposed in hover tooltips and analytics, but excluded from planar minimap positioning to prevent projection distortion.
