import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 1600, 900
FPS = 60
NUM_BALLS = 3000
GRAVITY = 0.01
FRICTION = 1  # Air resistance / Bounce dampening
ELASTICITY = 1  # Energy loss during ball-to-ball collision

# Grid Optimization
GRID_SIZE = 50  # Increased for higher density
CELL_W = WIDTH / GRID_SIZE
CELL_H = HEIGHT / GRID_SIZE

# Colors
BACKGROUND = (155, 155, 155)
PALETTE = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255),
    (255, 255, 100), (255, 100, 255), (100, 255, 255),
    (255, 165, 0), (138, 43, 226)
]

class Ball:
    def __init__(self, x, y, radius, color, base_image=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.mass = radius  # Simple mass proportional to radius
        
        # Image setup
        if base_image:
            self.image = pygame.transform.smoothscale(base_image, (radius * 2, radius * 2))
        else:
            self.image = None

    def update(self):
        # Apply Gravity
        self.vy += GRAVITY
        
        # Update Position
        self.x += self.vx
        self.y += self.vy

        # Wall Collisions
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -FRICTION
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -FRICTION

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -FRICTION
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -FRICTION
            # Prevent sticking to the floor
            if abs(self.vy) < 1:
                self.vy = 0

    def draw(self, screen):
        if self.image:
            # Draw image centered at (x, y)
            screen.blit(self.image, (int(self.x - self.radius), int(self.y - self.radius)))
        else:
            # Fallback to circle if no image
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            # Add a highlight
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x - self.radius/3), int(self.y - self.radius/3)), int(self.radius/4))

def resolve_collision(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    dist_sq = dx*dx + dy*dy
    rad_sum = b1.radius + b2.radius
    
    # Optimization: Use squared distance to avoid math.hypot (sqrt) if not colliding
    if dist_sq < rad_sum * rad_sum:
        distance = math.sqrt(dist_sq)
        if distance == 0: return # Prevent division by zero
        # 1. Resolve Overlap (anti-sticking)
        overlap = (b1.radius + b2.radius) - distance
        nx = dx / distance
        ny = dy / distance
        
        # Move balls apart based on mass (proportional to radius)
        total_radius = b1.radius + b2.radius
        b1.x -= nx * overlap * (b2.radius / total_radius)
        b1.y -= ny * overlap * (b2.radius / total_radius)
        b2.x += nx * overlap * (b1.radius / total_radius)
        b2.y += ny * overlap * (b1.radius / total_radius)

        # 2. Elastic Collision (Momentum transfer)
        # Normal vector
        # dot product of velocity and normal
        v1n = b1.vx * nx + b1.vy * ny
        v2n = b2.vx * nx + b2.vy * ny

        # Tangential vector (v1t, v2t remain unchanged in simple elastic collision)
        
        # New normal velocities (1D elastic collision formula)
        # m1v1 + m2v2 = m1v1' + m2v2'
        # v1 - v2 = -(v1' - v2')
        m1, m2 = b1.mass, b2.mass
        v1n_new = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
        v2n_new = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

        # Update velocities
        b1.vx += (v1n_new - v1n) * nx * ELASTICITY
        b1.vy += (v1n_new - v1n) * ny * ELASTICITY
        b2.vx += (v2n_new - v2n) * nx * ELASTICITY
        b2.vy += (v2n_new - v2n) * ny * ELASTICITY

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Physics Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    # Load Ball Image
    try:
        ball_img = pygame.image.load("Ball.png").convert_alpha()
    except:
        ball_img = None
        print("Warning: Ball.png not found, falling back to primitive circles.")

    balls = []
    for _ in range(NUM_BALLS):
        radius = random.randint(5, 10)
        x = random.randint(radius, WIDTH - radius)
        y = random.randint(radius, HEIGHT - radius)
        color = random.choice(PALETTE)
        balls.append(Ball(x, y, radius, color, ball_img))

    running = True
    frame_count = 0
    while running:
        import time
        start_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Add a ball on click
                radius = random.randint(15, 30)
                balls.append(Ball(event.pos[0], event.pos[1], radius, random.choice(PALETTE), ball_img))

        # Update Physics & Collision
        phys_start = time.time()
        for ball in balls:
            ball.update()

        # Spatial Partitioning (Grid Update)
        # Use a flat list or pre-allocated grid for better performance
        grid = [[] for _ in range(GRID_SIZE * GRID_SIZE)]
        for ball in balls:
            gx = int(ball.x // CELL_W)
            gy = int(ball.y // CELL_H)
            
            # Clamp to grid bounds
            gx = max(0, min(gx, GRID_SIZE - 1))
            gy = max(0, min(gy, GRID_SIZE - 1))
            
            grid[gy * GRID_SIZE + gx].append(ball)

        # Collision Check using Grid
        for gy in range(GRID_SIZE):
            for gx in range(GRID_SIZE):
                idx = gy * GRID_SIZE + gx
                cell_balls = grid[idx]
                if not cell_balls: continue
                
                # 1. Internal
                for i, b1 in enumerate(cell_balls):
                    for j in range(i + 1, len(cell_balls)):
                        resolve_collision(b1, cell_balls[j])
                    
                    # 2. Neighbors (Only check half to avoid duplicate pairs)
                    for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1)]:
                        nx, ny = gx + dx, gy + dy
                        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                            neighbor_balls = grid[ny * GRID_SIZE + nx]
                            for b2 in neighbor_balls:
                                resolve_collision(b1, b2)
        phys_time = (time.time() - phys_start) * 1000

        # Draw
        draw_start = time.time()
        screen.fill(BACKGROUND)
        for ball in balls:
            ball.draw(screen)
        
        # Display Diagnostics
        fps = int(clock.get_fps())
        draw_time = (time.time() - draw_start) * 1000
        
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
        phys_text = font.render(f"Physics: {phys_time:.2f}ms", True, (255, 255, 255))
        rend_text = font.render(f"Render: {draw_time:.2f}ms", True, (255, 255, 255))
        
        screen.blit(fps_text, (10, 10))
        screen.blit(phys_text, (10, 35))
        screen.blit(rend_text, (10, 60))
        
        # Terminal Logging every 60 frames
        frame_count += 1
        if frame_count % 60 == 0:
            print(f"FPS: {fps} | Physics: {phys_time:.2f}ms | Render: {draw_time:.2f}ms")

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
