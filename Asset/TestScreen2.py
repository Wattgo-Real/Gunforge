

<<<<<<< HEAD
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Start import Game

import Asset.Function as GF
from Asset.TestScreen1 import reset_screen1


def _format_time(t: float) -> str:
    minutes, seconds = divmod(int(t), 60)
    return f"{minutes:02d}:{seconds:02d}"


def _ensure_best(game: "Game"):
    if not hasattr(game, "best_record"):
        game.best_record = {"kills": 0, "time": 0.0, "damage": 0, "level": 1, "points": 0}
    if not hasattr(game, "total_points"):
        game.total_points = 0


def _commit_summary(game: "Game"):
    """Update best record and accumulated points exactly once per run."""
    summary = getattr(game, "run_summary", None)
    if not summary or summary.get("_committed"):
        return
    _ensure_best(game)
    best = game.best_record
    best["kills"] = max(best["kills"], summary["kills"])
    best["time"] = max(best["time"], summary["time"])
    best["damage"] = max(best["damage"], summary["damage"])
    best["level"] = max(best["level"], summary["level"])
    best["points"] = max(best["points"], summary["points"])
    game.total_points += summary["points"]
    summary["_committed"] = True


# 遊戲結束畫面 / Game-over and stats summary
def test_screen2(game: "Game", events):
    _ensure_best(game)
    _commit_summary(game)
    summary = getattr(game, "run_summary", None) or {"kills": 0, "time": 0.0, "damage": 0, "level": 1, "points": 0}

    # Buttons
    cx = game.screen_width // 2
    btn_w, btn_h = 240, 60
    play_btn = pygame.Rect(cx - btn_w - 30, game.screen_height - 140, btn_w, btn_h)
    menu_btn = pygame.Rect(cx + 30, game.screen_height - 140, btn_w, btn_h)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_btn.collidepoint(event.pos):
                reset_screen1(game)
                game.test_screen = 1
                return
            if menu_btn.collidepoint(event.pos):
                game.test_screen = 0
                return

    # Background
    game.screen.fill((18, 18, 28))

    # Title
    title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 64, bold=True)
    title_surf = title_font.render("RUN OVER", True, (240, 90, 90))
    game.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 80))

    # Summary panel
    panel_w, panel_h = 700, 360
    panel_x = cx - panel_w // 2
    panel_y = 200
    pygame.draw.rect(game.screen, (30, 30, 40), (panel_x, panel_y, panel_w, panel_h))
    pygame.draw.rect(game.screen, (180, 180, 200), (panel_x, panel_y, panel_w, panel_h), 2)

    rows = [
        ("Kills", f"{summary['kills']}", f"Best {game.best_record['kills']}"),
        ("Time", _format_time(summary['time']), f"Best {_format_time(game.best_record['time'])}"),
        ("Total Damage", f"{summary['damage']}", f"Best {game.best_record['damage']}"),
        ("Level", f"{summary['level']}", f"Best {game.best_record['level']}"),
        ("Points Earned", f"{summary['points']}", f"Total {game.total_points}"),
    ]

    for i, (label, value, best) in enumerate(rows):
        y = panel_y + 30 + i * 60
        label_surf = game.font.render(label, True, (220, 220, 220))
        value_surf = game.font.render(value, True, (255, 220, 120))
        best_surf = game.HUD_font.render(best, True, (160, 200, 255))
        game.screen.blit(label_surf, (panel_x + 40, y))
        game.screen.blit(value_surf, (panel_x + 320, y))
        game.screen.blit(best_surf, (panel_x + 480, y + 4))

    # Buttons
    GF.draw_button(game.screen, play_btn, "Play Again", font=game.font)
    GF.draw_button(game.screen, menu_btn, "Main Menu", font=game.font)
=======
# 可以在裡面測試不同項目
def test_screen2(self, events):
    # --- 1. Draw background. ---
    # Draw the background.
    self.DrawBackground()

    # --- 2. Draw player. ---
    self.DrawPlayer()

    # --- 3. Handles keyboard input (Player Movement). ---
    self.KeyBoardDetectionAndSetCamera()
>>>>>>> origin/main
