import os
import sys
import time
import math
import random
import uuid
import pygame

# Ensure we can import from Asset and root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Asset.GameSetting import GRID_CONFIG, ENTITY_TYPE, COLOR_CONFIG
from Asset.SpatialGrid import SpatialGrid, NoneGrid, Quadtree
from Asset.Enemies import Enemy
from Asset.Weapons import Bullet, BulletManager

class MockPlayer:
    def __init__(self):
        self.damage_multiplier = 1.0
        self.vel2D = pygame.Vector2(0, 0)
    def add_damage_dealt(self, dmg):
        pass
    def add_kill(self):
        pass

def _ensure_evaluation_state(game):
    if getattr(game, "_eval_initialized", False):
        return
    
    game.eval_methods = ["NoneGrid", "SpatialGrid", "Quadtree"]
    game.eval_ne_list = [100, 300, 600, 1200, 2000]
    game.eval_nb_list = [100, 500, 1000, 3000, 5000]
    
    game.eval_method_idx = 1  # Default to SpatialGrid
    game.eval_ne_idx = 0      # 100 enemies
    game.eval_nb_idx = 0      # 100 bullets
    
    game.eval_mock_player = MockPlayer()
    
    reset_evaluation(game)
    game._eval_initialized = True

def reset_evaluation(game):
    random.seed(42)
    import numpy as np
    np.random.seed(42)
    
    method = game.eval_methods[game.eval_method_idx]
    if method == "NoneGrid":
        game.spatial_grid_dict = NoneGrid()
    elif method == "SpatialGrid":
        game.spatial_grid_dict = SpatialGrid()
    elif method == "Quadtree":
        game.spatial_grid_dict = Quadtree()
        
    game.bullet_manager = BulletManager(spatial_grid_dict=game.spatial_grid_dict)
    game.bullet_manager.player = game.eval_mock_player
    
    ne = game.eval_ne_list[game.eval_ne_idx]
    nb = game.eval_nb_list[game.eval_nb_idx]
    
    # Spawn Enemies using the actual class
    game.eval_enemies = []
    for _ in range(ne):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(700, 900)
        pos = pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
        e = Enemy(pos, enemy_type=0)
        game.eval_enemies.append(e)
        game.spatial_grid_dict.register_entity(e)
        
    # Spawn Bullets
    for _ in range(nb):
        spawn_bullet(game)
        
    game.camera_position = pygame.Vector2(0, 0)
    
    # Metrics accumulator
    game.eval_fps = 60.0
    game.eval_logic_ms = 0.0
    game.eval_update_ms = 0.0
    game.eval_collision_ms = 0.0
    game.eval_checks = 0
    game.eval_checks_per_entity = 0
    game.eval_memory_kb = estimate_structure_memory(game.spatial_grid_dict) / 1024.0

def spawn_bullet(game):
    side = random.randint(0, 3)
    if side == 0:  # Top
        pos = pygame.Vector2(random.uniform(-1000, 1000), 1000)
    elif side == 1:  # Bottom
        pos = pygame.Vector2(random.uniform(-1000, 1000), -1000)
    elif side == 2:  # Left
        pos = pygame.Vector2(-1000, random.uniform(-1000, 1000))
    else:  # Right
        pos = pygame.Vector2(1000, random.uniform(-1000, 1000))
        
    direction = (pygame.Vector2(0, 0) - pos)
    if direction.length_squared() > 0:
        direction = direction.normalize()
    else:
        direction = pygame.Vector2(1, 0)
        
    new_bullet = game.bullet_manager.add_bullet([], 0, pos, direction)
    new_bullet.lifetime = 10

    

def estimate_structure_memory(partition_dict):
    seen = set()
    
    def get_size(obj):
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)
        
        if isinstance(obj, (Enemy, Bullet)):
            return sys.getsizeof(obj)
            
        size = sys.getsizeof(obj)
        
        if isinstance(obj, dict):
            size += sum(get_size(k) + get_size(v) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, pygame.Rect)):
            size += sum(get_size(item) for item in obj)
        elif hasattr(obj, '__dict__'):
            size += get_size(obj.__dict__)
        return size

    return get_size(partition_dict)

def _draw_evaluation_hud(game):
    # Dark panel overlay at the top left
    hud_width, hud_height = 420, 240
    hud_bg = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
    hud_bg.fill((20, 20, 30, 220))
    pygame.draw.rect(hud_bg, (100, 180, 255), hud_bg.get_rect(), 2)
    game.screen.blit(hud_bg, (20, 20))

    method = game.eval_methods[game.eval_method_idx]
    ne = game.eval_ne_list[game.eval_ne_idx]
    nb = game.eval_nb_list[game.eval_nb_idx]

    info_lines = [
        f"Spatial Method: {method}",
        f"Enemies (N_e):  {ne}",
        f"Bullets (N_b):  {nb}",
        f"FPS:            {game.eval_fps:.1f}",
        f"CPU Logic:      {game.eval_logic_ms:.2f} ms / frame",
        f"  - Update:     {game.eval_update_ms:.2f} ms",
        f"  - Collision:  {game.eval_collision_ms:.2f} ms",
        f"Checks/Entity:  {game.eval_checks_per_entity:.2f}",
        f"Memory Usage:   {game.eval_memory_kb:.2f} KB"
    ]

    for idx, line in enumerate(info_lines):
        color = (255, 255, 255)
        if "FPS" in line:
            color = (100, 255, 100) if game.eval_fps >= 50 else (255, 100, 100)
        elif "Method" in line:
            color = (255, 220, 120)
        
        text_surf = game.HUD_font.render(line, True, color)
        game.screen.blit(text_surf, (35, 30 + idx * 22))

    # Controls legend panel
    legend_width, legend_height = 420, 140
    legend_bg = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
    legend_bg.fill((20, 20, 30, 220))
    pygame.draw.rect(legend_bg, (150, 150, 150), legend_bg.get_rect(), 1)
    game.screen.blit(legend_bg, (20, 280))

    controls = [
        "Controls:",
        "[M] Toggle Partition Method",
        "[E] Toggle Enemy Count (N_e)",
        "[B] Toggle Bullet Count (N_b)",
        "[ESC] Return to Main Menu"
    ]
    for idx, ctrl in enumerate(controls):
        color = (255, 255, 255) if idx == 0 else (200, 200, 200)
        text_surf = game.HUD_font.render(ctrl, True, color)
        game.screen.blit(text_surf, (35, 290 + idx * 22))

def test_screen3(game, events):
    _ensure_evaluation_state(game)
    
    # Event handling
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.test_screen = 4
            elif event.key == pygame.K_m:
                game.eval_method_idx = (game.eval_method_idx + 1) % len(game.eval_methods)
                reset_evaluation(game)
            elif event.key == pygame.K_e:
                game.eval_ne_idx = (game.eval_ne_idx + 1) % len(game.eval_ne_list)
                reset_evaluation(game)
            elif event.key == pygame.K_b:
                game.eval_nb_idx = (game.eval_nb_idx + 1) % len(game.eval_nb_list)
                reset_evaluation(game)

    # Simulation Logic Step Timing
    t_start = time.perf_counter()
    
    # 1. Update entities
    # Enemies
    for e in game.eval_enemies:
        e.update(game.delta_time, pygame.Vector2(0, 0))
    
    # Bullets (managed by BulletManager)
    game.bullet_manager.update(game.delta_time, [])

    # 2. Update partitioning structure
    t_up_start = time.perf_counter()
    for e in game.eval_enemies:
        e.grid_pos = game.spatial_grid_dict.update_entity_pos(e, e.grid_pos, e.pos2D)
    
    if hasattr(game.spatial_grid_dict, '_rebuild_tree') and game.spatial_grid_dict.dirty:
        game.spatial_grid_dict._rebuild_tree()
    t_up_end = time.perf_counter()
    update_cost = (t_up_end - t_up_start) * 1000.0

    # 3. Collision detection & resolution
    t_coll_start = time.perf_counter()
    collision_checks = 0
    
    # Enemy vs Enemy collision
    for e1 in game.eval_enemies:
        nearby = game.spatial_grid_dict.get_entities_near_by_type(e1.pos2D, 1, range_cells=1)
        for e2 in nearby:
            if e1.uuid == e2.uuid:
                continue
            collision_checks += 1
            dist = e1.pos2D.distance_to(e2.pos2D)
            min_dist = e1.radius + e2.radius
            if dist < min_dist:
                overlap = min_dist - dist
                if dist > 0:
                    push_dir = (e1.pos2D - e2.pos2D).normalize()
                else:
                    push_dir = pygame.Vector2(1, 0)
                e1.pos2D += push_dir * (overlap * 0.5)
                e2.pos2D -= push_dir * (overlap * 0.5)

    # Bullet vs Enemy collision
    for bullet in game.bullet_manager.bullets:
        if bullet.isKill:
            continue
        nearby = game.spatial_grid_dict.get_entities_near_by_type(bullet.pos2D, 1, range_cells=1)
        for enemy in nearby:
            if enemy.uuid in bullet.hit_enemies:
                continue
            collision_checks += 1
            dist = bullet.pos2D.distance_to(enemy.pos2D)
            if dist < bullet.radius + enemy.radius + 5:
                bullet.triger_hit(enemy, effect_queue=[])
                break

    t_coll_end = time.perf_counter()
    collision_cost = (t_coll_end - t_coll_start) * 1000.0

    # Maintain constant entity counts by respawning
    ne_target = game.eval_ne_list[game.eval_ne_idx]
    for e in list(game.eval_enemies):
        if e.pos2D.length() < 20 or not e.alive:
            game.spatial_grid_dict.remove_entity(e.grid_pos, e.uuid)
            game.eval_enemies.remove(e)
    while len(game.eval_enemies) < ne_target:
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(700, 900)
        pos = pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
        e = Enemy(pos, enemy_type=0)
        game.eval_enemies.append(e)
        game.spatial_grid_dict.register_entity(e)

    nb_target = game.eval_nb_list[game.eval_nb_idx]
    while len(game.bullet_manager.bullets) < nb_target:
        spawn_bullet(game)

    t_end = time.perf_counter()
    logic_cost = (t_end - t_start) * 1000.0

    # Smooth the metrics for display stability
    alpha = 0.05
    fps_measured = game.clock.get_fps()
    game.eval_fps = (1 - alpha) * game.eval_fps + alpha * fps_measured if game.eval_fps > 0 else fps_measured
    game.eval_logic_ms = (1 - alpha) * game.eval_logic_ms + alpha * logic_cost
    game.eval_update_ms = (1 - alpha) * game.eval_update_ms + alpha * update_cost
    game.eval_collision_ms = (1 - alpha) * game.eval_collision_ms + alpha * collision_cost
    game.eval_checks = collision_checks
    
    total_entities = len(game.eval_enemies) + len(game.bullet_manager.bullets)
    game.eval_checks_per_entity = collision_checks / total_entities if total_entities > 0 else 0

    if game.total_frame_passed % 30 == 0:
        game.eval_memory_kb = estimate_structure_memory(game.spatial_grid_dict) / 1024.0

    # Draw step
    game.screen.fill((20, 20, 30))
    game.DrawBackground()

    # Draw bullets
    for bullet in game.bullet_manager.bullets:
        if bullet.isKill:
            continue
        bullet.draw(game.screen, game.to_screen)

    # Draw enemies using exact parameters from config
    for e in game.eval_enemies:
        screen_pos = game.to_screen(e.pos2D)
        if e.image:
            rect = e.image.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            game.screen.blit(e.image, rect)
        else:
            pygame.draw.circle(game.screen, e.color, screen_pos, e.radius)
            pygame.draw.circle(game.screen, (255, 255, 255), screen_pos, e.radius, 1)

    # Draw Center Target marker
    center_screen = game.to_screen(pygame.Vector2(0, 0))
    pygame.draw.circle(game.screen, (220, 60, 60), center_screen, 15, 2)
    pygame.draw.line(game.screen, (220, 60, 60), (center_screen.x - 25, center_screen.y), (center_screen.x + 25, center_screen.y), 2)
    pygame.draw.line(game.screen, (220, 60, 60), (center_screen.x, center_screen.y - 25), (center_screen.x, center_screen.y + 25), 2)

    # HUD & Legend
    _draw_evaluation_hud(game)
