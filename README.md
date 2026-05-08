## Hackmd Website
> https://hackmd.io/@yunshiuan/HyLdELvhbl

## 2026/05/04
### 新增槍械系統
- 在 test_screen1.py 內新增一個槍械與卡片系統，按 tab 切換槍械資訊介面，介面中可以看到槍械的資訊以及卡片列表，卡片可以選擇並放置到不同插槽中，滑鼠移動到附近可以看到卡片的資訊，目前卡片是以簡單的幾何形狀打造而成 (我發現使用 gemini 生成圖片反而會產生一些新的問題出現，所以我覺得在遊戲整個遊戲做完之前，不要去處理美術)。
- 場景中有新增一個測試的敵人，用於測試槍械子彈的傷害。
- GameSetting.py 中新增 UI_CONFIG、COLOR_CONFIG 還有一些子彈的屬性、能力、資訊，方便統一設定遊戲的數值。

## 2026/05/05

Simple Ui add and value Setting `GameSetting.py、Start.py TestScreen1.py TestScreen2.py`, and bastic Enemies and Boss designed `Enemies.py`
