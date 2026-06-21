## Hackmd Website
> https://hackmd.io/@yunshiuan/HyLdELvhbl

## 2026/05/04
### 新增槍械系統
- 在 test_screen1.py 內新增一個槍械與卡片系統，按 tab 切換槍械資訊介面，介面中可以看到槍械的資訊以及卡片列表，卡片可以選擇並放置到不同插槽中，滑鼠移動到附近可以看到卡片的資訊，目前卡片是以簡單的幾何形狀打造而成 (我發現使用 gemini 生成圖片反而會產生一些新的問題出現，所以我覺得在遊戲整個遊戲做完之前，不要去處理美術)。
- 場景中有新增一個測試的敵人，用於測試槍械子彈的傷害。
- GameSetting.py 中新增 UI_CONFIG、COLOR_CONFIG 還有一些子彈的屬性、能力、資訊，方便統一設定遊戲的數值。

## 2026/05/05

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