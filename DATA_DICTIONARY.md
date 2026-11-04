# LILA BLACK Telemetry — Data Dictionary & Dataset Specification

**Version:** 1.0  
**Data Scope:** February 10, 2026 – February 14, 2026 (5 days production gameplay)  
**Game Title:** LILA BLACK (Extraction Shooter)  
**Source Archive:** `player_data.zip` (1,243 files, ~89,104 events)

---

## 1. File & Storage Architecture

Each file represents a single participant's (human player or bot) telemetry recording within a single match instance.

- **Storage Format:** Apache Parquet (Snappy compression, columnar binary). Note: Files omit the `.parquet` extension and end with `.nakama-0`.
- **Naming Convention:** `{user_id}_{match_id}.nakama-0`
  - Human player filename example: `f4e072fa-b7af-4761-b567-1d95b7ad0108_b71aaad8-aa62-4b3a-8534-927d4de18f22.nakama-0`
  - Bot filename example: `1440_d7e50fad-fb7a-4ed4-932f-e4ca9ff0c97b.nakama-0`
- **Folder Organization:**
  - `February_10/` (437 files)
  - `February_11/` (293 files)
  - `February_12/` (268 files)
  - `February_13/` (166 files)
  - `February_14/` (79 files, partial day)
  - `minimaps/` (Top-down visual maps)

---

## 2. Telemetry Schema & Column Specifications

| Column Name | PyArrow Type | Pandas Dtype | Nullable | Description & Domain |
|---|---|---|---|---|
| `user_id` | `string` | `object` / `string` | No (0 nulls) | Unique identifier for the player or AI bot. UUID string (36 chars) for human players; numeric string (e.g. "1440") for bots. |
| `match_id` | `string` | `object` / `string` | No (0 nulls) | Unique identifier of the match instance. Carries the game server suffix `.nakama-0`. |
| `map_id` | `string` | `object` / `category` | No (0 nulls) | Identifier of the game map. Values: `AmbroseValley`, `GrandRift`, `Lockdown`. |
| `x` | `float32` | `float32` | No (0 nulls) | In-game horizontal world coordinate (East-West axis). Units: game world meters. |
| `y` | `float32` | `float32` | No (0 nulls) | In-game vertical elevation coordinate (Height above sea level). **Do NOT use for 2D minimap mapping.** |
| `z` | `float32` | `float32` | No (0 nulls) | In-game forward/depth world coordinate (North-South axis). Corresponds to the 2D vertical map axis. |
| `ts` | `timestamp[ms]` | `datetime64[ms]` / `int64` | No (0 nulls) | Telemetry timestamp. Raw integer values represent Unix epoch seconds (`1770754537` = `2026-02-10 20:15:37 UTC`). Sample rate is ~0.2 Hz (~every 5 seconds). |
| `event` | `binary` (bytes) | `object` (`bytes` / decoded `str`) | No (0 nulls) | Raw UTF-8 bytes defining event category. Must be decoded with `.decode('utf-8')`. |

---

## 3. Event Types & Semantics

| Event Name | Raw Byte Value | Frequency | % of Total | Category | Semantic Description |
|---|---|---|---|---|---|
| `Position` | `b'Position'` | 51,347 | 57.63% | Movement | Periodic positional heartbeat sampled for human players (~every 5 seconds). |
| `BotPosition` | `b'BotPosition'` | 21,712 | 24.37% | Movement | Periodic positional heartbeat sampled for AI bots (~every 5 seconds). |
| `Loot` | `b'Loot'` | 12,885 | 14.46% | Economy | Player collected/looted an in-game item or container. |
| `BotKill` | `b'BotKill'` | 2,415 | 2.71% | Combat | A human player killed an AI bot. |
| `BotKilled` | `b'BotKilled'` | 700 | 0.79% | Combat | A human player was killed by an AI bot. |
| `KilledByStorm` | `b'KilledByStorm'` | 39 | 0.04% | Environment | A player died outside the safe zone due to the advancing one-directional storm. |
| `Kill` | `b'Kill'` | 3 | <0.01% | Combat (PvP) | A human player killed another human player. |
| `Killed` | `b'Killed'` | 3 | <0.01% | Combat (PvP) | A human player was killed by another human player. |

**Classification Rule for Combat:**
- Total Kills by Humans: `BotKill` (2,415) + `Kill` (3) = **2,418**
- Total Deaths of Humans: `BotKilled` (700) + `Killed` (3) + `KilledByStorm` (39) = **742**
- Total Combat Engagements: 3,121 events

---

## 4. Map Coordinate System & Calibration

The game world uses a 3D Cartesian system where `X` is East(+)/West(-), `Y` is elevation (up/down), and `Z` is North(+)/South(-). The 2D minimaps correspond to the `(X, Z)` plane.

### Map Calibration Matrix

| Map ID | Scale Factor ($S$) | Origin $X$ ($O_x$) | Origin $Z$ ($O_z$) | Minimap Image Dimensions | Aspect Ratio | Observed $X$ Range | Observed $Z$ Range |
|---|---|---|---|---|---|---|---|
| **AmbroseValley** | 900.0 | -370.0 | -473.0 | 4320 × 4320 (RGBA) | 1:1 (Square) | [-324.97, 301.79] | [-380.01, 360.76] |
| **GrandRift** | 581.0 | -290.0 | -290.0 | 2160 × 2158 (RGBA) | ~1:1 (Square) | [-225.90, 256.62] | [-194.00, 170.11] |
| **Lockdown** | 1000.0 | -500.0 | -500.0 | 9000 × 9000 (RGB) | 1:1 (Square) | [-406.63, 348.36] | [-285.10, 329.24] |

### Transformation Formula

$$u = \frac{x - O_x}{S}$$
$$v = \frac{z - O_z}{S}$$

Converting normalized $u, v \in [0, 1]$ to pixel coordinates on an image of width $W$ and height $H$ (with origin $(0,0)$ at top-left):

$$\text{pixel}_x = u \times W$$
$$\text{pixel}_y = (1.0 - v) \times H$$

For normalized canvas rendering (Plotly/SVG), mapping to $u \in [0, 1]$ and $v \in [0, 1]$ directly avoids resolution dependencies.

---

## 5. Human vs. Bot Entity Identification

1. **Identifier Pattern:**
   - **Human:** Standard UUID v4 format (36 characters with hyphens, e.g. `f4e072fa-b7af-4761-b567-1d95b7ad0108`).
   - **Bot:** Integer string representation (e.g. `1440`, `382`, `1455`).
2. **Event Type Alignment:**
   - Humans generate `Position`, `Kill`, `Killed`, `BotKill`, `BotKilled`, `Loot`, `KilledByStorm`.
   - Bots generate `BotPosition` (and are victims/assailants recorded in `BotKill`/`BotKilled`).
3. **Classification Function:**
   ```python
   def is_bot(user_id: str) -> bool:
       return not ('-' in str(user_id) and len(str(user_id)) > 20)
   ```

---

## 6. Data Quality & Nuance Audit

1. **Zero Nulls:** All columns across all 89,104 records contain 0 null/NaN values.
2. **Zero Corrupted Files:** All 1,243 files are valid, readable Parquet tables.
3. **Timestamp Unit Encoding:** Parquet schema metadata specifies `timestamp[ms]`, but values are stored as Unix epoch seconds (e.g. `1770754537` = `2026-02-10 20:15:37 UTC`). Converting to real datetime requires treating raw integers as seconds or multiplying by 1,000 before parsing as milliseconds.
4. **Elevation Isolation:** The `y` column represents elevation/height (ranging from ~8m to ~162m). It must be excluded from 2D planar map projections to avoid distortion.
5. **Image Resolutions:** Raw minimap assets have differing native dimensions (AmbroseValley is 4320×4320, GrandRift is 2160×2158, Lockdown is 9000×9000). The application dynamically scales or normalizes them to ensure ultra-fast browser rendering without memory bloat.
