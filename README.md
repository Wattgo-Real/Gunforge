# Gunforge

A 2D Vampire Survivors-style top-down survival roguelike shooter built in Python using Pygame. The game features a dynamic grid/quadtree-based spatial partitioning system, a customizable gun card crafting system (stackable gun cards in inventory slots), pathfinding systems (including Flow Fields, A*, and Dijkstra), and utility-based Boss AI behaviors.

---

## Software Requirements

To run the game and its evaluation modes, you need:
- **Python**: 3.11
- **Pygame**: 2.6.1
- **numpy**: 2.X.X

---

## Installation Instructions

1. **Clone or download**
    ```bash
    git clone https://github.com/Wattgo-Real/Gunforge.git
    ```
2. **Install dependencies**:
   ```bash
   pip install pygame numpy
   ```

---

## Execution Steps

- **Start Main Game & Evaluation GUI**:
  ```bash
  python Start.py
  ```

---

## Controls

### Main Game Controls
- **Movement**: `W` `A` `S` `D` keys to move the player character.
- **Shoot**: `Left Click` and hold to fire in the direction of the mouse cursor.
- **Inventory & Skill Cards**: Press `TAB` to open/close the gun/backpack inventory overlay.
  - Hover the mouse over a card to view its description.
  - Drag and drop (or select) cards to place them into the gun slots to modify gun attributes/skills.
  - Hover over a slotted card to see slot information.
- **Shop / Upgrade Screen**: Access via the shop option in the main loop to upgrade player stats using banked points.

### Evaluation 1 (Pathfinding Stress Test) Controls
- `Left` / `Right` Arrow Keys: Toggle pathfinding algorithms (`Steering`, `A*`, `Dijkstra`, `Flow Field`).
- `Up` / `Down` Arrow Keys: Toggle enemy count ($N$ = 10, 30, 60, 120, 200, 300).
- `P`: Pause / Resume simulation.
- `R`: Reset the current pathfinding simulation run.
- `ESC`: Return to the Evaluation Menu.

### Evaluation 2 (Boss Decision Policy Duel) Controls
- `M`: Toggle simulated player opponent mode (`Behavior` AI vs. `Scripted` movement).
- `R`: Reset all metrics and run a new sweep of duels.
- `ESC`: Return to the Evaluation Menu.

### Evaluation 3 (Spatial Partitioning Stress Test) Controls
- `M`: Toggle spatial partitioning algorithm (`NoneGrid` / No Partitioning, `SpatialGrid`, `Quadtree`).
- `E`: Toggle enemy count ($N_e$ = 100, 300, 600, 1200, 2000).
- `B`: Toggle bullet count ($N_b$ = 100, 500, 1000, 3000, 5000).
- `ESC`: Return to the Evaluation Menu.

---

## Important Settings & Parameters

All core configuration constants and balance values are centralized in [Asset/GameSetting.py](file:///c:/Users/User/Desktop/Gunforge/Asset/GameSetting.py):
- **`GAME_CONFIG`**: Controls basic player attributes (health, range, speeds, starting points), chunk sizes, shop costs, and flow field settings.
- **`BULLET_CONFIG`**: Configurations for different bullet types and their respective properties.
- **`GRID_CONFIG`**: Parameters for spatial partitioning grid cells and spatial partitioning limits.
- **`COLOR_CONFIG`**: Color definitions for the UI and entity rendering.
- **`UI_CONFIG`**: Layout guidelines and metrics for screens and overlays.

---

## How to Reproduce the Main Demo

1. Execute `python Start.py`.
2. Click **Play** on the main menu.
3. Move around the map, defeat incoming enemies, collect experience orbs to level up and gain points, and stand on altars to obtain temporary buffs.
4. Press `TAB` to customize your gun behavior by slotting collected cards.
5. Survive for 5 minutes (300 seconds) until the boss spawns, and defeat the boss to complete the run.

---

## How to Reproduce Experiments or Evaluation Results

The evaluation modes can be run through the main application:
1. Run `python Start.py`.
2. Click **Evaluation Mode** on the main menu.
3. Select the evaluation run you wish to reproduce:
   - **Evaluation 1 (Pathfinding)**: Evaluates efficiency (frame/path computation times in ms, stuck counts, target reached count) of different navigation models. The results are printed to stdout as:
     `[EVAL1_RESULT] method=... N=... frames=... frame_ms=...`
   - **Evaluation 2 (Boss Decision Policy)**: Simulates duels between different boss controllers (`FSM`, `Behavior Tree`, `Goal-Oriented Behavior/Utility AI`) and the player. The results are printed to stdout as:
     `[EVAL2_RESULT] method=... boss_dps=... dodge_success=...`
   - **Evaluation 3 (Spatial Partitioning)**: Compares performance metrics of broad-phase collision detection using `NoneGrid`, `SpatialGrid`, and `Quadtree`. Prints results after reaching target frames:
     `[EVAL3_RESULT] method=... enemies=... bullets=... fps=... cpu_ms=...`

---

## Known Limitations

- **Interactive Diagnostic Tools**: The current evaluation modes are interactive diagnostic tools, not automated statistical experiments. They display smoothed metrics during play, but the repository does not yet export CSV logs, confidence intervals, or saved benchmark runs. Therefore, the current report focuses on implemented methodology and qualitative analysis rather than claiming precise numeric improvements.
- **Boss Decision Policy Tuning**: The production boss now uses the same utility-style policy as the GOB evaluation controller, but the tuning is still preliminary. In the current low-HP Evaluation 2 setup, both the revised BT and GOB produce varied attack selection, but GOB has lower direct damage pressure, so its weights and attack damage should be further tuned against human play rather than only against the FSM behavior-player.
- **Flow Field & Grid Constraints**: The flow field is rebuilt in a local radius around the player and is designed for enemies pursuing one moving target. It would need extension for multiple targets, cooperative formations, dynamic obstacle carving, or enemies with different navigation goals. Similarly, the uniform grid uses wrapped indexing and fixed cell sizes, which are efficient for the current prototype but would need more careful treatment for a larger world with highly variable entity sizes.
- **Spatial Partitioning Scalability**: Although spatial partitioning is highly powerful and its memory footprint is rarely a concern given the standard specifications of modern computers, scalability remains a critical constraint. In a 3D environment, if the number of subdivisions per axis scales up to 1,000 or more, the required number of spatial cells skyrockets to $1000^3$. This exponential growth consumes an immense amount of memory, demonstrating that this approach still has its practical limits.
- **Prototype Status**: Finally, the game is still a prototype. Balance, art consistency, accessibility, sound, data export, automated tests, and long-run memory behavior require more work before the system could be considered production-ready.

---

## Development History

### Hackmd Website
> https://hackmd.io/@yunshiuan/HyLdELvhbl

### 2026/05/04
#### 新增槍械系統
- 在 test_screen1.py 內新增一個槍械與卡片系統，按 tab 切換槍械資訊介面，介面中可以看到槍械的資訊以及卡片列表，卡片可以選擇並放置到不同插槽中，滑鼠移動到附近可以看到卡片的資訊，目前卡片是以簡單的幾何形狀打造而成 (我發現使用 gemini 生成圖片反而會產生一些新的問題出現，所以我覺得在遊戲整個遊戲做完之前，不要去處理美術)。
- 場景中有新增一個測試的敵人，用於測試槍械子彈的傷害。
- GameSetting.py 中新增 UI_CONFIG、COLOR_CONFIG 還有一些子彈的屬性、能力、資訊，方便統一設定遊戲的數值。

### 2026/05/05
Simple Ui add and value Setting `GameSetting.py、Start.py TestScreen1.py TestScreen2.py`, and bastic Enemies and Boss designed `Enemies.py`

### 2026/05/10
- Add Spatial Partitioning Grid.
- Add the enemy vs enemy collision detection (Based on Spatial Partitioning Grid).

### 2026/05/17
- Adjust the obstacle detection logic (Based on Spatial Partitioning Grid).
- Add the obstacle vs bullet collision detection (Based on Spatial Partitioning Grid).
- Add levelup 3 random cards selection system.
- Adjust Gun and Bullet System.
- Add more cards.

### 2026/05/24
- Add Quadtree and No Partitioning.
- Adjust Gun and Bullet System.
- Add more cards.

### 2026/05/31
- Add more cards
- Add Evaluation3.py to compare the efficiency of different spatial partitioning methods.

### 2026/06/06
- Add obstacles enemys boss Images
- Update Evaluation1 and Evaluation2

### 2026/06/16
Make some numerical adjustments (Altar size, enemy health)

### 2026/06/18
- adjust enemy probability of generation and health,damage,drops
- update e2 player Range distance
- add player hp regen
- add shop page

### 2026/06/20
- adjust game balance
> - After 60s, the enemy spawn rate will gradually increase (quadruple after 300s, but return to the original spawn rate after the boss spawns).
> - After 150 seconds, spawn a ring of 16 chasers around the player every 30 seconds.
> - After 150 seconds, the enemy's health will begin to increase (double after 5 minutes).
- fix some bug