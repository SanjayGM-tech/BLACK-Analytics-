# LILA BLACK — Game Analytics & Level Design Insights

**Telemetry Scope:** February 10–14, 2026 (89,104 events | 796 matches | 3 maps)  
**Author:** Senior Product & Game Analytics Engineer  
**Target Audience:** LILA Games Level Design Team, Combat Designers, and Product Leadership  

---

## Executive Summary

Through systematic spatial, combat, and temporal analysis of 5 days of production telemetry across **Ambrose Valley**, **Lockdown**, and **Grand Rift**, three critical operational patterns emerge:

1. **Severe Western Congestion vs. Northeast Map Desertion** in Ambrose Valley (73.3% western traffic vs. 9.8% northeast traffic).
2. **Disproportionate Storm Lethality in Lockdown and Grand Rift** (nearly 3× higher death rate to the storm than Ambrose Valley due to interior chokepoint bottlenecks).
3. **Overwhelming PvE Bot Saturation with Near-Zero PvP Encounters** (99.88% of all eliminations are bot-related; only 3 human-on-human kills recorded across 796 matches).

---

## Insight 1: Severe Western Flank Congestion vs. Northeast Map Desertion in Ambrose Valley

### 1. What Caught Our Attention
When rendering the spatial traffic density heatmap across all 61,013 events in **Ambrose Valley** (the flagship map representing 68.5% of all gameplay), the map displays an extreme asymmetrical traffic split. Players heavily favor the western side of the map, while large swathes of the northeastern perimeter remain virtually untouched throughout the 5 days of recorded gameplay.

### 2. Supporting Statistics
- **Total Ambrose Valley Telemetry Events:** 61,013 rows across 566 matches.
- **Northwest (NW) Quadrant:** 20,754 events (**34.0%**).
- **Southwest (SW) Quadrant:** 23,973 events (**39.3%**).
- **Combined Western Half (NW + SW):** 44,727 events (**73.3%** of all map activity).
- **Northeast (NE) Quadrant:** 5,995 events (**9.8%** of map activity).
- **Southeast (SE) Quadrant:** 10,291 events (**16.9%** of map activity).
- **Traffic Ratio:** Players spend **7.46× more time** in the western corridors than in the northeastern sector.

### 3. Relevant Map & Coordinates
- **Map:** Ambrose Valley ($S=900, O_x=-370, O_z=-473$).
- **High-Traffic Corridor:** Normalized coordinates $u \in [0.10, 0.45], v \in [0.15, 0.70]$ (World $X \in [-280, 35], Z \in [-338, 157]$).
- **Ignored Dead Zone:** Normalized coordinates $u \in [0.60, 0.95], v \in [0.55, 0.95]$ (World $X \in [170, 485], Z \in [22, 382]$).

### 4. Evidence from the Dataset
- Loot pickup density follows the exact same skew: **7,268 out of 9,955 loot events (73.0%)** in Ambrose Valley occurred in the western quadrants.
- Combat follows suit: **1,318 out of 1,799 kills (73.3%)** are concentrated in the western half.
- The northeast quadrant generated only 894 loot pickups and 183 kills over 5 days.

### 5. Possible Explanation (Hypothesis vs. Fact)
- **Proven Fact:** Players and bots are overwhelmingly concentrated in the western corridors, where almost three-quarters of all loot collection and combat occurs.
- **Hypothesis:** Initial player insertion/spawn points may be biased toward the west, and high-value extraction beacons appear to spawn along the western river/valley spine. Players have little gameplay incentive to navigate the longer, open traversals of the northeast without guaranteed high-tier rewards.

### 6. Actionable Recommendation for Level Design
1. **Redistribute High-Tier Loot POIs:** Move at least 25% of high-grade weapon and armor spawns from the western ridge into the northeastern compounds ($u \in [0.65, 0.85], v \in [0.60, 0.85]$).
2. **Anchor Guaranteed Extraction Beacons in the Northeast:** Rotate extraction beacon spawn algorithms to activate extraction points in the NE sector when the storm originates from the SW.
3. **Add Natural Cover Corridors:** Introduce trenches, rock formations, or abandoned vehicles between central Ambrose Valley and the NE POIs to reduce the traversal risk across open ground.

### 7. Expected Metrics That May Improve
- Quadrant traffic balance: Target NE quadrant activity to rise from 9.8% to 20–25%.
- Average match exploration area per player increased by 30%.
- Reduction in immediate post-spawn congestion deaths in the western corridor.

### 8. Why This Insight Matters
Developing 3D game environments is expensive. Approximately 30% of the playable area of Ambrose Valley is currently wasted space that players never experience, creating artificial repetition for veteran players and reducing perceived map variety.

---

## Insight 2: Chokepoint Bottlenecks Drive 3× Higher Storm Casualties in Lockdown & Grand Rift

### 1. What Caught Our Attention
The one-directional storm is designed as a pacing mechanic to force players toward extraction. However, comparing death distributions across the three maps reveals that players are nearly **3 times more likely to die to the storm in Lockdown and Grand Rift** than in Ambrose Valley.

### 2. Supporting Statistics
- **Ambrose Valley:** 17 storm deaths out of 505 total deaths (**3.37%**).
- **Lockdown:** 17 storm deaths out of 185 total deaths (**9.19%** — **2.73× higher** than Ambrose Valley).
- **Grand Rift:** 5 storm deaths out of 52 total deaths (**9.62%** — **2.85× higher** than Ambrose Valley).
- **Spatial Concentration in Lockdown:** 100% of the 17 storm deaths in Lockdown cluster inside a tight central-north band:
  - Mean $u = 0.55$, Mean $v = 0.54$.
  - Coordinate bounding box: $u \in [0.15, 0.82], v \in [0.39, 0.75]$.

### 3. Relevant Map & Coordinates
- **Map:** Lockdown ($S=1000, O_x=-500, O_z=-500$).
- **Lethal Chokepoint Zone:** World $X \in [-350, 320], Z \in [-110, 250]$ (Minimap canvas pixel coordinates $X \in [154, 840], Y \in [256, 625]$).

### 4. Evidence from the Dataset
- In Ambrose Valley (a wide, open valley map), players successfully outrun or flank the advancing storm, resulting in only 3.37% storm deaths.
- In Lockdown (an urban, interior-heavy CQB map), players frequently enter combat in the central corridors ($u \in [0.45, 0.65], v \in [0.45, 0.65]$). When the storm wave arrives, trajectory tracks show sudden deceleration and erratic backtracking before `KilledByStorm` events trigger.

### 5. Possible Explanation (Hypothesis vs. Fact)
- **Proven Fact:** Storm mortality is significantly higher on compact and urban maps, clustered specifically around interior structures in the central band.
- **Hypothesis:** Lockdown's narrow interior doors, stairwells, and dead-end alleys prevent players from disengaging cleanly when the storm approaches. Players engaged in firefights with bots lose track of the storm timer and cannot navigate exterior escape routes in time.

### 6. Actionable Recommendation for Level Design
1. **Pacing & Warning Timers:** Increase storm approach warning audio and UI cue lead-time on Lockdown by **15 seconds** (from standard timing) to compensate for complex indoor pathfinding.
2. **Corridor Widening & Breakthrough Doors:** Add breachable doors or secondary window mantling options along the central east-west complex ($u \approx 0.50–0.60$) so players are not trapped in single-exit corridors.
3. **Emergency Mobility Drops:** Spawn temporary speed-boost consumables or storm-shield stims near high-risk central interior zones.

### 7. Expected Metrics That May Improve
- Reduction in Lockdown storm mortality from 9.19% to below 4.5%.
- Increase in extraction success rate from 68% to 80% on Lockdown.
- Reduction in player frustration and non-combat wipes.

### 8. Why This Insight Matters
Dying to another player or a challenging AI bot feels earned; dying to a wall because you couldn't find a doorway while the storm consumes you is one of the top causes of churn in extraction shooters.

---

## Insight 3: PvE Bot Dominance and Extreme Scarcity of PvP Engagements

### 1. What Caught Our Attention
LILA BLACK is described as an extraction shooter featuring PvPvE combat. However, analyzing all combat elimination events across 5 days reveals that human players almost never fight each other. The live game environment operates almost exclusively as a **cooperative/solo PvE experience against AI bots**.

### 2. Supporting Statistics
Across all 89,104 events and 796 matches:
- **Human Kills of AI Bots (`BotKill`):** **2,415** (**99.88%** of all kills).
- **Human Kills of Human Players (`Kill`):** **3** (**0.12%** of all kills).
- **AI Bot Kills of Humans (`BotKilled`):** **700** (**99.57%** of combat deaths).
- **Human-on-Human Deaths (`Killed`):** **3** (**0.43%** of combat deaths).
- **Bot-to-Human Kill Ratio:** Humans kill bots at a ratio of $2,415 : 700 = \mathbf{3.45 : 1}$.
- **Average Participant Split Per Match:** Matches contain an average of **1.14 human players** and **13.8 bots** (over 92% bot population per match).
- **Telemetry Volume:** Bot movement events (`BotPosition`: 21,712) and bot combat interactions dominate server processing, while human player trajectories rarely intersect.

### 3. Relevant Maps & Scope
- Observed universally across **Ambrose Valley**, **Grand Rift**, and **Lockdown**.
- In Ambrose Valley (566 matches), only 2 PvP kills were recorded in 5 days.
- In Lockdown (171 matches), only 1 PvP kill was recorded.
- In Grand Rift (59 matches), **0 PvP kills** were recorded.

### 4. Evidence from the Dataset
- When examining match files, over 80% of matches contain only **1 single human player** placed into a match with 10 to 15 bots.
- In the rare matches that contained multiple humans (e.g. match `ff73c97b-3b34-4836-a8a1-47b2f94dd77c` with 3 humans), player paths show that humans navigated separate quadrants and extracted without ever coming within line-of-sight of each other.

### 5. Possible Explanation (Hypothesis vs. Fact)
- **Proven Fact:** The current matchmaking and telemetry data represents an almost pure PvE combat loop.
- **Hypothesis:** During this test period (Feb 10–14, 2026), matchmaking rules may have prioritized low queue times over lobby pooling, spawning matches as soon as a single player queued and filling remaining slots with bots. Additionally, map extraction beacons are dispersed so widely that separate players have no focal point forcing confrontation.

### 6. Actionable Recommendation for Level & Game Design
1. **Dynamic High-Value Target (HVT) Beacons:** Implement a central map event (e.g. "Supply Airdrop" or "HVT Boss Extraction") that triggers at minute 3 of the match, displaying a visible smoke signal or ping that incentivizes players to converge.
2. **Consolidated Extraction Phase:** Instead of 4 independent extraction zones, restrict late-match extraction to a single active landing zone with a 60-second countdown, creating natural PvP tension.
3. **Matchmaker Lobby Thresholds:** Adjust matchmaking server rules to hold players in a 30-second pre-match lobby until at least 3–4 human players are grouped, rather than launching single-player instances with 15 bots.

### 7. Expected Metrics That May Improve
- PvP engagement rate increased from 0.12% to 15–20% of combat encounters.
- Significant increase in session tension, clip-worthy emergent moments, and player retention.
- Reduction in server hosting costs by reducing the number of redundant single-human match instances.

### 8. Why This Insight Matters
Extraction shooters thrive on high-stakes player-versus-player tension. If players realize every opponent is an AI bot with predictable behaviors, long-term retention rapidly degrades. Designing maps with convergence vectors is essential to fulfilling the core game vision.
