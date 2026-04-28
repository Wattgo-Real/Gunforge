

import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Start import Game

# 可以在裡面測試不同項目，目前使用當中: Wattgo
def test_screen1(self : "Game", events):
    mouse_pos_world = self.to_world(pygame.mouse.get_pos())
    self.player.face_direction = (pygame.Vector2(mouse_pos_world) - self.player.pos2D).normalize()

    # --- 1. Player Movement & Weapon Update. ---
    self.PlayerUpdate()

    # --- 2. Draw background. ---
    # Draw the background.
    self.DrawBackground()

    # --- 3. Draw player, bullet, weapon, enemy. ---
    self.DrawLayer1()

    # self.DrawLayer2() 
    # self.DrawLayer3() 
    # self.DrawLayer4() 

