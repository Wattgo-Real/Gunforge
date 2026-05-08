import pygame
import sys
import numpy as np
np.random.seed(42)

import Asset.Function as GF
import Asset.TestScreen1 as TS1
import Asset.TestScreen2 as TS2

from Asset.Player import Player

class Game():
    def __init__(self):
        # Initialize pygame (must be called before using any pygame functions)
        pygame.init()

        # Set the window title
        pygame.display.set_caption("Game")

        # Screen size
        self.screen_width : int = 1600
        self.screen_height : int = 900

        # Create the game window 
        self.screen : pygame.Surface = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen_center : pygame.Vector2 = pygame.Vector2(self.screen_width//2, self.screen_height//2)

        # Create a clock object to control the frame rate
        self.clock : pygame.time.Clock = pygame.time.Clock()

        # Create a font object for rendering text
        self.font : pygame.font.SysFont = pygame.font.SysFont(["consolas", "monaco", "monospace"], 24)
        self.HUD_font : pygame.font.SysFont = pygame.font.SysFont(["consolas", "monaco", "monospace"], 16)

        # Init camera position.
        self.camera_position : pygame.Vector2 = pygame.Vector2(0,0)

        # Init player.
        ball_color : tuple = (0, 150, 255)
        self.player : Player = Player(position = pygame.Vector2(0,0), radius = 15, color = ball_color)
        
        # Background grid image.
        self.background : pygame.Surface = pygame.image.load("./Img/grid_1000x1000.png").convert_alpha()   # size: 1000 x 1000

        # Time per frame.
        self.delta_time : float = 1/60

        # Record number of frames passed since of start the game.
        self.total_frame_passed : int = 0

        # Record time passed since of start the game.
        self.now_time : float = 0

        self.test_screen = 0
        self.selected_slot_info = None
        self.gun_info = False

        # Persistent meta-progression
        self.best_record = {"kills": 0, "time": 0.0, "damage": 0, "level": 1, "points": 0}
        self.total_points = 0
        self.run_summary = None

    def _draw_main_menu(self, events):
        self.screen.fill((20, 20, 30))

        title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 96, bold=True)
        title_surf = title_font.render("GUNFORGE", True, (255, 220, 120))
        self.screen.blit(title_surf, ((self.screen_width - title_surf.get_width()) // 2, 140))

        sub_surf = self.font.render("Vampire-Survivors-style with stackable gun cards", True, (200, 200, 220))
        self.screen.blit(sub_surf, ((self.screen_width - sub_surf.get_width()) // 2, 240))

        cx = self.screen_width // 2
        play_btn = pygame.Rect(cx - 150, 360, 300, 70)
        quit_btn = pygame.Rect(cx - 150, 460, 300, 70)
        info_lines = [
            "WASD to move   |   Left click to fire   |   TAB to open gun/inventory",
            "Survive, kill enemies, collect XP orbs, stand on altars for buffs.",
            f"Boss appears at 5:00.   |   Total points banked: {self.total_points}",
        ]

        GF.draw_button(self.screen, play_btn, "Play", font=self.font)
        GF.draw_button(self.screen, quit_btn, "Quit", font=self.font)

        info_y = 580
        for line in info_lines:
            line_surf = self.HUD_font.render(line, True, (200, 200, 200))
            self.screen.blit(line_surf, ((self.screen_width - line_surf.get_width()) // 2, info_y))
            info_y += 24

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_btn.collidepoint(event.pos):
                    self.gun_info = False
                    TS1.reset_screen1(self)
                    self.test_screen = 1
                elif quit_btn.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

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
        """
        Fill the screen, 這裡直接幫我替換到你想設計的地圖背景
        """
        self.screen.fill((30, 30, 30))
            
        LD = self.camera_position - self.screen_center
        LeftDown = np.floor(LD / 1000).astype(np.int32)
        RightUp = np.floor((LD + np.array([self.screen_width, self.screen_height])) / 1000).astype(np.int32)
        grid_points = [pygame.Vector2(x, y) for x in range(LeftDown[0], RightUp[0]+1) for y in range(LeftDown[1], RightUp[1]+1)]

        for i in range(len(grid_points)):
            self.screen.blit(self.background, self.to_screen(1000 * grid_points[i]) - pygame.Vector2(0, 1000))

    def DrawLayer1(self):
        """
        Draw Layer 1.
        """
        # --- 1. Draw bullet. ---
        for weapon in self.player.weapon_list:
            if weapon is None:
                continue
            for bullet in weapon.bullets:
                bullet.draw(self.screen, self.to_screen)

        # --- 2. Draw player. ---
        # Draw Trajectory Trail
        if len(self.player.history_position) > 1:
            points = [self.to_screen(p) for p in self.player.history_position]
            if len(points) >= 2:
                pygame.draw.lines(self.screen, (70, 70, 70), False, points, 2)

        # Draw the Ball (Player)
        # Using a simple circle for the "ball"
        pygame.draw.circle(self.screen, self.player.color, self.to_screen(self.player.pos2D), self.player.radius)
        
        # Add a little "glow" or detail
        pygame.draw.circle(self.screen, (255, 255, 255), self.to_screen(self.player.pos2D), self.player.radius, 2)

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

    def PlayerUpdate(self, mouse_clicked : bool = False):
        """
        If self.KeyBoardControl is True, the target position can be controlled by arrow keys, and the camera will follow the target. \n
        If self.KeyBoardControl is False, the camera will follow the Main Agent.
        """
        # Get current keyboard state (continuous input)
        keys = pygame.key.get_pressed()

        # Get current mouse state
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Update weapon
        self.player.UpdateWeapon(self.delta_time, fire = mouse_buttons[0], trigger_feedback = mouse_clicked)

        # Update position based on arrow key input
        acc_dir = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            acc_dir.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            acc_dir.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            acc_dir.y += 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            acc_dir.y -= 1
        self.player.Update(self.delta_time, acc_dir)

        # Set the camera position to follow the target
        self.camera_position = self.player.pos2D


if __name__ == '__main__':
    game = Game()
    game.Start()