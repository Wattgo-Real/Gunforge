import pygame
import sys
from Player import Player

def main():
    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pygame Controllable Ball")

    # Colors
    bg_color = (30, 30, 30)
    ball_color = (0, 150, 255)
    trail_color = (0, 255, 255, 100) # Cyan with alpha

    # Initialize Player
    # Center of screen
    player = Player(width // 2, height // 2, radius=15, color=ball_color)

    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. Delta time calculation
        dt = clock.tick(60) / 1000.0 # dt in seconds

        # 2. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 3. Input Handling (Acceleration direction)
        keys = pygame.key.get_pressed()
        acc_dir = pygame.Vector2(0, 0)
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            acc_dir.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            acc_dir.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            acc_dir.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            acc_dir.y += 1

        # 4. Update Player Physics
        player.Update(dt, acc_dir)

        # 5. Boundary Check (Simple teleport wrap or bounce)
        # Bouncing logic
        if player.pos2D.x - player.radius < 0:
            player.pos2D.x = player.radius
            player.vel2D.x *= -0.5 # Bounce back with some energy loss
        elif player.pos2D.x + player.radius > width:
            player.pos2D.x = width - player.radius
            player.vel2D.x *= -0.5

        if player.pos2D.y - player.radius < 0:
            player.pos2D.y = player.radius
            player.vel2D.y *= -0.5
        elif player.pos2D.y + player.radius > height:
            player.pos2D.y = height - player.radius
            player.vel2D.y *= -0.5

        # 6. Rendering
        screen.fill(bg_color)

        # Draw Trajectory Trail
        if len(player.history_position) > 1:
            points = [(p.x, p.y) for p in player.history_position]
            if len(points) >= 2:
                pygame.draw.lines(screen, (70, 70, 70), False, points, 2)

        # Draw the Ball (Player)
        # Using a simple circle for the "ball"
        pygame.draw.circle(screen, player.color, (int(player.pos2D.x), int(player.pos2D.y)), player.radius)
        
        # Add a little "glow" or detail
        pygame.draw.circle(screen, (255, 255, 255), (int(player.pos2D.x), int(player.pos2D.y)), player.radius, 2)

        # Update Display
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
