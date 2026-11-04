# Coordinate Validation & Mathematical Transformation Report

**Scope:** Full audit of all 89,104 telemetry events across all 3 game maps.

## 1. Mathematical Transformation Matrix

| Map Name | Scale ($S$) | Origin $X$ ($O_x$) | Origin $Z$ ($O_z$) | Canvas Width | Canvas Height |
|---|---|---|---|---|---|
| **Ambrose Valley** (`AmbroseValley`) | 900.0 | -370.0 | -473.0 | 1024 px | 1024 px |
| **Grand Rift** (`GrandRift`) | 581.0 | -290.0 | -290.0 | 1024 px | 1024 px |
| **Lockdown** (`Lockdown`) | 1000.0 | -500.0 | -500.0 | 1024 px | 1024 px |

### Transformation Formulas
$$u = \frac{x - O_x}{S}, \quad v = \frac{z - O_z}{S}$$
$$\text{pixel}_x = u \times W, \quad \text{pixel}_y = (1.0 - v) \times H$$

### Inverse Formulas (Canvas Pixel to In-Game World)
$$u = \frac{\text{pixel}_x}{W}, \quad v = 1.0 - \frac{\text{pixel}_y}{H}$$
$$x = u \times S + O_x, \quad z = v \times S + O_z$$

---

## 2. Empirical Coordinate Bounds per Map

| Map | Total Events | Min $X$ | Max $X$ | Min $Z$ | Max $Z$ | Min $U$ | Max $U$ | Min $V$ | Max $V$ | In-Bounds % |
|---|---|---|---|---|---|---|---|---|---|---|
| **AmbroseValley** | 61,013 | -324.97 | 301.79 | -380.01 | 360.76 | 0.0500 | 0.7464 | 0.1033 | 0.9264 | **100.00%** |
| **GrandRift** | 6,853 | -225.90 | 256.62 | -194.00 | 170.11 | 0.1103 | 0.9408 | 0.1652 | 0.7919 | **100.00%** |
| **Lockdown** | 21,238 | -406.63 | 348.36 | -285.10 | 329.24 | 0.0934 | 0.8484 | 0.2149 | 0.8292 | **100.00%** |

---

## 3. Boundary & Landmark Verification

### A. Official README Reference Verification (Ambrose Valley)
- **Input World Position:** $x = -301.45, z = -355.55$
- **Configuration:** Origin $= (-370.0, -473.0)$, Scale $= 900.0$
- **Calculated UV:** $u = 0.0762, v = 0.1305$
- **Calculated Pixels:** $\text{pixel}_x = 78.0, \text{pixel}_y = 890.4$
- **Expected in README:** $\text{pixel}_x = 78, \text{pixel}_y = 890$
- **Discrepancy:** $\Delta x = 0.0053\text{ px}, \Delta y = 0.0320\text{ px}$ (Exact integer match).

### B. Inverse Round-Trip Error Analysis
1,000 randomly sampled telemetry points were converted from World $\rightarrow$ Pixel $\rightarrow$ World.
- **Max Round-Trip Error X:** `5.684342e-14` meters
- **Max Round-Trip Error Z:** `5.684342e-14` meters
- **Conclusion:** Round-trip floating point precision is accurate within $10^{-11}$ meters.

### C. Outlier & Anomaly Audit
- Out-of-bounds events ($u, v < 0$ or $u, v > 1$): **0 events** across all 89,104 telemetry samples.
- Null/NaN coordinates: **0 events**.
- Vertical elevation column ($y$) distribution: Observed range $[8.14, 162.67]$ meters. Confirmed excluded from planar minimap positioning to prevent projection skew.