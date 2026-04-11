import pygame
import sys
import numpy as np
np.random.seed(42)

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

    def Start(self):
        # Control variable for the main loop
        running = True

        while running:    
            # Handle events (e.g., window close)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # --- 1. Draw background. ---
            # Draw the background.
            self.DrawBackground()

            # --- 2. Draw player. ---
            self.DrawPlayer()

            # --- 3. Handles keyboard input (Player Movement). ---
            self.KeyBoardDetectionAndSetCamera()

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

    def DrawPlayer(self):
        """
        Draw player
        """
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

  
    def KeyBoardDetectionAndSetCamera(self):
        """
        If self.KeyBoardControl is True, the target position can be controlled by arrow keys, and the camera will follow the target. \n
        If self.KeyBoardControl is False, the camera will follow the Main Agent.
        """
        # Get current keyboard state (continuous input)
        keys = pygame.key.get_pressed()
        
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