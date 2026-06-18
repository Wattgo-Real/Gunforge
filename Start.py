import pygame
import sys
import os
import numpy as np
np.random.seed(42)

from Asset.FontCompat import install_pygame_font_compat
install_pygame_font_compat(pygame)

from Asset.ImageLoader import load_image_surface
import Asset.Function as GF
import Asset.TestScreen1 as TS1
import Asset.TestScreen2 as TS2
import Asset.Evaluation1 as EV1
import Asset.Evaluation2 as EV2
import Asset.Evaluation3 as EV3

from Asset.Player import Player

class Game():
    DESIGN_WIDTH = 1600
    DESIGN_HEIGHT = 900
    WINDOW_MARGIN = 0.92
    PLAYER_SPRITE_PATH = "./Img/player_sprite.png"
    PLAYER_SPRITE_HEIGHT = 118
    PLAYER_SPRITE_BASE_ANGLE = 0

    def __init__(self):
        os.environ.setdefault("SDL_VIDEO_CENTERED", "1")

        # Initialize pygame (must be called before using any pygame functions)
        pygame.init()

        # Set the window title
        pygame.display.set_caption("Game")

        # Screen size. Fit the 16:9 design into the current desktop so the
        # window is not larger than the user's visible screen area.
        self.screen_width, self.screen_height = self._get_window_size()

        # Create the game window
        self.screen : pygame.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen_center : pygame.Vector2 = pygame.Vector2(self.screen_width//2, self.screen_height//2)

        # Create a clock object to control the frame rate
        self.clock : pygame.time.Clock = pygame.time.Clock()

        # Create a font object for rendering text
        self.font : pygame.font.SysFont = pygame.font.SysFont(["consolas", "monaco", "monospace"], 24)
        self.mid_font : pygame.font.SysFont = pygame.font.SysFont(["consolas", "monaco", "monospace"], 20)
        self.HUD_font : pygame.font.SysFont = pygame.font.SysFont(["consolas", "monaco", "monospace"], 16)

        # Init camera position.
        self.camera_position : pygame.Vector2 = pygame.Vector2(0,0)

        # Background image tile.
        try:
            self.background : pygame.Surface = load_image_surface("./Img/background.png")
        except (OSError, pygame.error):
            self.background = self._create_grid_background()
        self.background_tile_size = pygame.Vector2(self.background.get_size())

        # Time per frame.
        self.delta_time : float = 1/60

        # Record number of frames passed since of start the game.
        self.total_frame_passed : int = 0

        # Record time passed since of start the game.
        self.now_time : float = 0

        self.test_screen = 0
        self.selected_slot_info = None
        self.gun_info = False

        # Using SpatialGrid for spatial partitioning.
        self.partition_method = "SpatialGrid"   # "NoneGrid" or "Quadtree" or "SpatialGrid"

        # Persistent meta-progression
        self.best_record = {"kills": 0, "time": 0.0, "damage": 0, "level": 1, "points": 0}
        self.total_points = 0
        self.run_summary = None
        self._player_sprite_source = None
        self._player_sprite_scaled = None
        self._player_sprite_failed = False

    def _get_window_size(self):
        try:
            desktop_w, desktop_h = pygame.display.get_desktop_sizes()[0]
        except (IndexError, pygame.error):
            desktop_w, desktop_h = self.DESIGN_WIDTH, self.DESIGN_HEIGHT

        scale = min(
            1.0,
            (desktop_w * self.WINDOW_MARGIN) / self.DESIGN_WIDTH,
            (desktop_h * self.WINDOW_MARGIN) / self.DESIGN_HEIGHT,
        )
        width = max(1, int(self.DESIGN_WIDTH * scale))
        height = max(1, int(self.DESIGN_HEIGHT * scale))
        return width, height

    def _create_grid_background(self):
        background = pygame.Surface((1000, 1000), pygame.SRCALPHA)
        background.fill((0, 0, 0, 0))
        for pos in range(0, 1001, 100):
            color = (60, 60, 60) if pos % 500 else (85, 85, 85)
            pygame.draw.line(background, color, (pos, 0), (pos, 1000), 1)
            pygame.draw.line(background, color, (0, pos), (1000, pos), 1)
        return background

    def _get_player_sprite(self):
        if self._player_sprite_failed:
            return None
        if self._player_sprite_scaled is not None:
            return self._player_sprite_scaled

        try:
            self._player_sprite_source = load_image_surface(self.PLAYER_SPRITE_PATH)
        except (OSError, pygame.error, ValueError):
            self._player_sprite_failed = True
            return None

        width, height = self._player_sprite_source.get_size()
        scale = self.PLAYER_SPRITE_HEIGHT / max(1, height)
        self._player_sprite_scaled = pygame.transform.smoothscale(
            self._player_sprite_source,
            (max(1, int(width * scale)), self.PLAYER_SPRITE_HEIGHT),
        )
        return self._player_sprite_scaled

    def _draw_player_sprite(self):
        screen_pos = self.to_screen(self.player.pos2D)
        sprite = self._get_player_sprite()

        if sprite is None:
            pygame.draw.circle(self.screen, self.player.color, screen_pos, self.player.radius)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, self.player.radius, 2)
            return

        direction = pygame.Vector2(self.player.face_direction)
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        screen_direction = pygame.Vector2(direction.x, -direction.y)
        angle = -screen_direction.as_polar()[1] + self.PLAYER_SPRITE_BASE_ANGLE
        rotated = pygame.transform.rotozoom(sprite, angle, 1.0)
        self.screen.blit(rotated, rotated.get_rect(center=(int(screen_pos.x), int(screen_pos.y))))

    def _blit_centered(self, surface, center_y):
        rect = surface.get_rect(center=(self.screen.get_rect().centerx, center_y))
        self.screen.blit(surface, rect)

    def _draw_main_menu(self, events):
        self.screen.fill((20, 20, 30))
        center_x = self.screen.get_rect().centerx
        h = self.screen_height

        title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 96, bold=True)
        title_surf = title_font.render("GUNFORGE", True, (255, 220, 120))
        self._blit_centered(title_surf, int(h * 0.20))

        sub_surf = self.font.render("Vampire-Survivors-style with stackable gun cards", True, (200, 200, 220))
        self._blit_centered(sub_surf, int(h * 0.29))

        play_btn = pygame.Rect(0, 0, 300, 70)
        eval_btn = pygame.Rect(0, 0, 300, 70)
        quit_btn = pygame.Rect(0, 0, 300, 70)
        play_btn.center = (center_x, int(h * 0.41))
        eval_btn.center = (center_x, int(h * 0.51))
        quit_btn.center = (center_x, int(h * 0.61))
        info_lines = [
            "WASD to move   |   Left click to fire   |   TAB to open gun/inventory",
            "Survive, kill enemies, collect XP orbs, stand on altars for buffs.",
            f"Boss appears at 5:00.   |   Total points banked: {self.total_points}",
        ]

        GF.draw_button(self.screen, play_btn, "Play", font=self.font)
        GF.draw_button(self.screen, eval_btn, "Evaluation Mode", font=self.font)
        GF.draw_button(self.screen, quit_btn, "Quit", font=self.font)

        info_y = int(h * 0.72)
        for line in info_lines:
            line_surf = self.HUD_font.render(line, True, (200, 200, 200))
            self._blit_centered(line_surf, info_y)
            info_y += 24

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.collidepoint(event.pos):
                    self.gun_info = False
                    TS1.reset_screen1(self)
                    self.test_screen = 1
                elif eval_btn.collidepoint(event.pos):
                    self.test_screen = 4
                elif quit_btn.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _draw_evaluation_menu(self, events):
        self.screen.fill((20, 20, 30))
        center_x = self.screen.get_rect().centerx
        h = self.screen_height

        title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 64, bold=True)
        title_surf = title_font.render("EVALUATION MODE", True, (100, 180, 255))
        self._blit_centered(title_surf, int(h * 0.20))

        btn_eval1 = pygame.Rect(0, 0, 300, 70)
        btn_eval2 = pygame.Rect(0, 0, 300, 70)
        btn_eval3 = pygame.Rect(0, 0, 300, 70)
        btn_back = pygame.Rect(0, 0, 300, 70)
        btn_eval1.center = (center_x, int(h * 0.34))
        btn_eval2.center = (center_x, int(h * 0.45))
        btn_eval3.center = (center_x, int(h * 0.56))
        btn_back.center = (center_x, int(h * 0.67))

        GF.draw_button(self.screen, btn_eval1, "Evaluation 1", font=self.font)
        GF.draw_button(self.screen, btn_eval2, "Evaluation 2", font=self.font)
        GF.draw_button(self.screen, btn_eval3, "Evaluation 3", font=self.font)
        GF.draw_button(self.screen, btn_back, "Back", font=self.font)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_eval1.collidepoint(event.pos):
                    self.test_screen = 5
                elif btn_eval2.collidepoint(event.pos):
                    self.test_screen = 6
                elif btn_eval3.collidepoint(event.pos):
                    self.test_screen = 3
                elif btn_back.collidepoint(event.pos):
                    self.test_screen = 0

    def Start(self):
        # Control variable for the main loop
        running = True

        while running:
            # Handle events (e.g., window close)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            if self.test_screen == 0:
                self._draw_main_menu(events)
            elif self.test_screen == 1:
                TS1.test_screen1(self, events)
            elif self.test_screen == 2:
                TS2.test_screen2(self, events)
            elif self.test_screen == 3:
                EV3.test_screen3(self, events)
            elif self.test_screen == 4:
                self._draw_evaluation_menu(events)
            elif self.test_screen == 5:
                EV1.test_screen_eval1(self, events)
            elif self.test_screen == 6:
                EV2.test_screen_eval2(self, events)


            # Update the display (render everything to the screen)
            pygame.display.flip()

            # Limit the frame rate to 60 FPS
            self.total_frame_passed += 1
            self.clock.tick(60)
            self.now_time = self.total_frame_passed * self.delta_time

        # Clean up and exit
        pygame.quit()
        sys.exit()

    def to_screen(self, pos):
        """
        Convert world coordinates to screen coordinates.
        """
        pos = pos + self.screen_center - self.camera_position
        return pygame.Vector2(pos.x, self.screen_height - pos.y)

    def to_world(self, pos):
        """
        Convert screen coordinates to world coordinates.
        """
        pos = pygame.Vector2(pos[0], self.screen_height - pos[1])
        return pos - self.screen_center + self.camera_position

    def DrawBackground(self):
        self.screen.fill((30, 30, 30))

        tile_w = self.background_tile_size.x
        tile_h = self.background_tile_size.y
        LD = self.camera_position - self.screen_center
        LeftDown = np.floor(np.array([LD.x / tile_w, LD.y / tile_h])).astype(np.int32)
        RightUp = np.floor(np.array([
            (LD.x + self.screen_width) / tile_w,
            (LD.y + self.screen_height) / tile_h,
        ])).astype(np.int32)
        grid_points = [pygame.Vector2(x, y) for x in range(LeftDown[0], RightUp[0]+1) for y in range(LeftDown[1], RightUp[1]+1)]

        for i in range(len(grid_points)):
            tile_origin = pygame.Vector2(tile_w * grid_points[i].x, tile_h * grid_points[i].y)
            self.screen.blit(self.background, self.to_screen(tile_origin) - pygame.Vector2(0, tile_h))

    def DrawLayer1(self):
        # --- 1. Draw bullet. ---
        for bullet in self.bullet_manager.bullets:
            if bullet.isKill:
                continue
            bullet.draw(self.screen, self.to_screen)

        # --- 2. Draw player. ---
        # Draw Trajectory Trail
        if len(self.player.history_position) > 1:
            points = [self.to_screen(p) for p in self.player.history_position]
            if len(points) >= 2:
                pygame.draw.lines(self.screen, (70, 70, 70), False, points, 2)

        self._draw_player_sprite()

        # --- 3. Draw Player Feedback Messages ---
        if self.player.weapon_error_timer > 0:
            # Position above player's head
            world_pos_above = self.player.pos2D + pygame.Vector2(0, self.player.radius + 15)
            screen_pos = self.to_screen(world_pos_above)

            # Render text
            alpha = min(255, int(255 * (self.player.weapon_error_timer / 0.5))) if self.player.weapon_error_timer < 0.5 else 255
            color = (255, 100, 100) # Reddish

            error_surf = self.HUD_font.render(self.player.weapon_error_msg, True, color)
            # Create a surface for alpha if needed, but simple blit with HUD_font is usually fine.
            # Pygame's render doesn't support per-pixel alpha easily without a temporary surface if using .set_alpha()
            # For simplicity, we just blit it.

            text_rect = error_surf.get_rect(center=(screen_pos.x, screen_pos.y))
            self.screen.blit(error_surf, text_rect)


if __name__ == '__main__':
    game = Game()
    game.Start()
