import math
import random
import heapq

import pygame

from Asset.GameSetting import BOSS_CONFIG, ENEMY_CONFIG, GAME_CONFIG, GRID_CONFIG
from Asset.GameSetting import ENTITY_TYPE
from Asset.ImageLoader import load_image_surface
from Asset.SpatialGrid import SpatialGrid
import uuid

_ENEMY_IMAGE_CACHE = {}
FLOW_NEIGHBORS_8 = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
)
BOSS_ACTIONS = ("Ring", "Spread", "Spiral", "Dash", "Charge")
BOSS_GOB_WEIGHTS = {
    "Ring": 1.05,
    "Spread": 1.00,
    "Spiral": 0.90,
    "Dash": 1.05,
    "Charge": 1.20,
}
BOSS_GOB_REPEAT_PENALTY = 0.75


def _get_enemy_image(path, sprite_height):
    if not path or sprite_height <= 0:
        return None

    key = (path, sprite_height)
    if key in _ENEMY_IMAGE_CACHE:
        return _ENEMY_IMAGE_CACHE[key]

    try:
        image = load_image_surface(path)
        width, height = image.get_size()
        scale = sprite_height / height
        sprite_width = max(1, int(width * scale))
        sprite_height = max(1, int(sprite_height))
        image = pygame.transform.smoothscale(image, (sprite_width, sprite_height))
    except (OSError, pygame.error, ValueError):
        image = None

    _ENEMY_IMAGE_CACHE[key] = image
    return image


class FlowFieldNavigator:
    def __init__(self):
        self.cell_size = GAME_CONFIG["flow_field_cell_size"]
        self.radius_cells = GAME_CONFIG["flow_field_radius_cells"]
        self.refresh_interval = GAME_CONFIG["flow_field_refresh_interval"]
        self.obstacle_padding = GAME_CONFIG["flow_field_obstacle_padding"]
        self.timer = 0.0
        self.player_cell = None
        self.origin_cell = (0, 0)
        self.grid_size = self.radius_cells * 2 + 1
        self.blocked = set()
        self.flow = {}

    def reset(self):
        self.timer = 0.0
        self.player_cell = None
        self.origin_cell = (0, 0)
        self.blocked.clear()
        self.flow.clear()

    def update(self, delta_time, player_pos, obstacles):
        current_cell = self._world_to_cell(player_pos)
        self.timer -= delta_time
        if (
            self.player_cell == current_cell
            and self.timer > 0
            and self.flow
        ):
            return

        self.player_cell = current_cell
        self.timer = self.refresh_interval
        self._build(player_pos, obstacles)

    def direction_at(self, pos):
        world_cell = self._world_to_cell(pos)
        local = self._to_local(world_cell)
        return self.flow.get(local)

    def _build(self, player_pos, obstacles):
        self.origin_cell = (
            self.player_cell[0] - self.radius_cells,
            self.player_cell[1] - self.radius_cells,
        )
        self.blocked = self._blocked_cells(obstacles)
        goal = self._nearest_walkable(self._to_local(self.player_cell))

        frontier = [(0.0, goal)]
        dist = {goal: 0.0}
        while frontier:
            curr_cost, curr = heapq.heappop(frontier)
            if curr_cost > dist[curr]:
                continue

            for dx, dy in FLOW_NEIGHBORS_8:
                nxt = (curr[0] + dx, curr[1] + dy)
                if not self._is_walkable(nxt):
                    continue
                if dx != 0 and dy != 0:
                    if not self._is_walkable((curr[0] + dx, curr[1])):
                        continue
                    if not self._is_walkable((curr[0], curr[1] + dy)):
                        continue

                new_cost = curr_cost + (math.sqrt(2.0) if dx != 0 and dy != 0 else 1.0)
                if nxt not in dist or new_cost < dist[nxt]:
                    dist[nxt] = new_cost
                    heapq.heappush(frontier, (new_cost, nxt))

        flow = {}
        for cell, cell_cost in dist.items():
            if cell == goal:
                continue
            best = None
            best_cost = cell_cost
            for dx, dy in FLOW_NEIGHBORS_8:
                nxt = (cell[0] + dx, cell[1] + dy)
                if nxt in dist and dist[nxt] < best_cost:
                    best = nxt
                    best_cost = dist[nxt]
            if best is not None:
                direction = pygame.Vector2(best[0] - cell[0], best[1] - cell[1])
                if direction.length_squared() > 0:
                    flow[cell] = direction.normalize()

        self.flow = flow

    def _blocked_cells(self, obstacles):
        blocked = set()
        for obs in obstacles:
            half = obs.size / 2
            min_cell = self._world_to_cell(
                pygame.Vector2(
                    obs.pos2D.x - half.x - self.obstacle_padding,
                    obs.pos2D.y - half.y - self.obstacle_padding,
                )
            )
            max_cell = self._world_to_cell(
                pygame.Vector2(
                    obs.pos2D.x + half.x + self.obstacle_padding,
                    obs.pos2D.y + half.y + self.obstacle_padding,
                )
            )
            min_local = self._to_local(min_cell)
            max_local = self._to_local(max_cell)
            for lx in range(max(0, min_local[0]), min(self.grid_size, max_local[0] + 1)):
                for ly in range(max(0, min_local[1]), min(self.grid_size, max_local[1] + 1)):
                    blocked.add((lx, ly))
        return blocked

    def _nearest_walkable(self, cell):
        if self._is_walkable(cell):
            return cell

        queue = [cell]
        seen = {cell}
        for curr in queue:
            for dx, dy in FLOW_NEIGHBORS_8[:4]:
                nxt = (curr[0] + dx, curr[1] + dy)
                if nxt in seen:
                    continue
                if self._is_walkable(nxt):
                    return nxt
                if self._in_bounds(nxt):
                    seen.add(nxt)
                    queue.append(nxt)
        return (self.radius_cells, self.radius_cells)

    def _world_to_cell(self, pos):
        return (
            math.floor(pos.x / self.cell_size),
            math.floor(pos.y / self.cell_size),
        )

    def _to_local(self, world_cell):
        return (
            world_cell[0] - self.origin_cell[0],
            world_cell[1] - self.origin_cell[1],
        )

    def _in_bounds(self, cell):
        return 0 <= cell[0] < self.grid_size and 0 <= cell[1] < self.grid_size

    def _is_walkable(self, cell):
        return self._in_bounds(cell) and cell not in self.blocked


class DamageNumber:
    def __init__(self, damage, position, color=(255, 255, 100)):
        self.damage = damage
        self.pos2D = pygame.Vector2(position)
        self.pos2D += pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
        self.velocity = pygame.Vector2(0, 50)
        self.timer = 1.0
        self.alpha = 255
        self.color = color

    def update(self, delta_time):
        self.pos2D.y += self.velocity.y * delta_time
        self.timer -= delta_time
        self.alpha = max(0, int(255 * (self.timer / 1.0)))

    def draw(self, screen, game):
        font = game.HUD_font
        text_surf = font.render(str(int(self.damage)), True, self.color)
        text_surf.set_alpha(self.alpha)
        screen_pos = game.to_screen(self.pos2D)
        screen.blit(text_surf, (screen_pos.x - text_surf.get_width() // 2, screen_pos.y))


class EnemyBullet:
    def __init__(self, pos2D, vel2D, damage, lifetime=4.0, radius=6, color=(255, 100, 100)):
        self.uuid = uuid.uuid4()    # unique identifier of the spatial partitioning
        self.pos2D = pygame.Vector2(pos2D)
        self.vel2D = pygame.Vector2(vel2D)
        self.damage = damage
        self.lifetime = lifetime
        self.timer = 0
        self.radius = radius
        self.color = color
        self.alive = True

    def update(self, delta_time):
        self.pos2D += self.vel2D * delta_time
        self.timer += delta_time
        if self.timer >= self.lifetime:
            self.alive = False

    def draw(self, screen, game):
        screen_pos = game.to_screen(self.pos2D)
        pygame.draw.circle(screen, self.color, screen_pos, self.radius)
        pygame.draw.circle(screen, (255, 255, 255), screen_pos, self.radius, 1)


class Enemy:
    def __init__(self, position, enemy_type=0, hp_mul=1.0, dmg_mul=1.0, is_boss=False):
        cfg = BOSS_CONFIG if is_boss else ENEMY_CONFIG[enemy_type]
        self.uuid = uuid.uuid4()
        self.entity_type = ENTITY_TYPE["enemy"]

        self.enemy_type = enemy_type
        self.cfg = cfg
        self.is_boss = is_boss
        self.pos2D = pygame.Vector2(position)
        self.radius = cfg["radius"]
        self.color = cfg["color"]
        self.image = _get_enemy_image(cfg.get("image_path"), cfg.get("sprite_height", self.radius * 4))
        self.max_hp = cfg["max_hp"] * hp_mul
        self.hp = self.max_hp
        self.speed = cfg["speed"]
        self.damage = cfg["damage"] * dmg_mul
        self.attack_cooldown = cfg["attack_cooldown"]
        self.attack_timer = random.uniform(0, self.attack_cooldown)
        self.xp_drop = cfg.get("xp_drop", 1)
        self.ai = cfg["ai"]
        self.preferred_distance = cfg.get("preferred_distance", 0)
        self.bullet_speed = cfg.get("bullet_speed", 200)
        self.enemy_bullets = []
        self.damage_numbers = []
        self.alive = True
        self.reward_claimed = False
        self.dash_state = "approach"
        self.dash_timer = random.uniform(1.0, 2.5)
        self.boss_phase_timer = 0.0
        self.boss_charge_state = "aim"
        self.boss_charge_timer = 0.0
        self.boss_charge_count = 0
        self.boss_charge_direction = pygame.Vector2(1, 0)
        self.boss_action = None
        self.boss_action_timer = 0.0
        self.boss_action_duration = 0.0
        self.boss_action_cooldown = 0.0
        self.boss_action_fire_timer = 0.0
        self.boss_action_end_fired = False
        self.boss_last_action = None
        self.boss_orbit_sign = 1 if random.random() > 0.5 else -1
        self.boss_dash_velocity = pygame.Vector2(0, 0)
        self.boss_spiral_angle = random.random() * math.tau
        self.boss_score_snapshot = {name: 0.0 for name in BOSS_ACTIONS}

    def take_damage(self, damage):
        self.hp -= damage
        self.damage_numbers.append(DamageNumber(damage, self.pos2D.copy()))
        if self.hp <= 0:
            self.alive = False

    def _move_towards(self, target_pos, delta_time, speed=None, flow_field=None):
        speed = self.speed if speed is None else speed
        direction = flow_field.direction_at(self.pos2D) if flow_field is not None else None
        if direction is None:
            diff = target_pos - self.pos2D
            if diff.length_squared() == 0:
                return
            direction = diff.normalize()
        self.pos2D += direction * speed * delta_time

    def _move_at_distance(self, target_pos, delta_time, distance, flow_field=None):
        diff = target_pos - self.pos2D
        d = diff.length()
        if d == 0:
            return
        direction = diff.normalize()
        if d > distance + 30:
            self._move_towards(target_pos, delta_time, self.speed, flow_field)
        elif d < distance - 30:
            self.pos2D -= direction * self.speed * delta_time
        else:
            perp = pygame.Vector2(-direction.y, direction.x)
            self.pos2D += perp * self.speed * 0.5 * delta_time

    def _shoot_at(self, target_pos, speed_mul=1.0, damage_mul=1.0, color=(255, 80, 80), radius=6):
        diff = target_pos - self.pos2D
        if diff.length_squared() == 0:
            return None
        vel = diff.normalize() * self.bullet_speed * speed_mul
        return EnemyBullet(self.pos2D, vel, self.damage * damage_mul, lifetime=3.5, radius=radius, color=color)

    def update(self, delta_time, player_pos, flow_field=None):
        self.attack_timer = max(0, self.attack_timer - delta_time)

        if self.ai == "chase":
            self._move_towards(player_pos, delta_time, flow_field=flow_field)
        elif self.ai == "runner":
            self.dash_timer -= delta_time
            if self.dash_state == "approach":
                self._move_towards(player_pos, delta_time, flow_field=flow_field)
                if self.dash_timer <= 0:
                    self.dash_state = "dash"
                    self.dash_timer = 0.5
            else:
                self._move_towards(player_pos, delta_time, self.speed * 2.4, flow_field)
                if self.dash_timer <= 0:
                    self.dash_state = "approach"
                    self.dash_timer = random.uniform(1.5, 3.0)
        elif self.ai == "shooter":
            self._move_at_distance(player_pos, delta_time, self.preferred_distance, flow_field)
            if self.attack_timer <= 0:
                bullet = self._shoot_at(player_pos)
                if bullet:
                    self.enemy_bullets.append(bullet)
                    self.attack_timer = self.attack_cooldown
        elif self.ai == "boss":
            self._update_boss(delta_time, player_pos, flow_field)

        for b in self.enemy_bullets[:]:
            b.update(delta_time)
            if not b.alive:
                self.enemy_bullets.remove(b)

        for dn in self.damage_numbers[:]:
            dn.update(delta_time)
            if dn.timer <= 0:
                self.damage_numbers.remove(dn)

    def _update_boss(self, delta_time, player_pos, flow_field=None):
        self.boss_phase_timer += delta_time
        self.boss_action_cooldown = max(0.0, self.boss_action_cooldown - delta_time)
        self.boss_action_timer += delta_time

        if (
            self.boss_action is None
            or (
                self.boss_action_cooldown <= 0
                and self.boss_action_timer >= self.boss_action_duration
            )
        ):
            self._start_boss_action(self._choose_boss_action(player_pos), player_pos)

        self._run_boss_action(delta_time, player_pos, flow_field)

    def _choose_boss_action(self, player_pos):
        distance = self.pos2D.distance_to(player_pos)
        hp_ratio = max(0.0, self.hp / max(1.0, self.max_hp))
        low_hp = 1.0 - hp_ratio
        near_score = max(0.0, (230.0 - distance) / 120.0)
        mid_score = max(0.0, 1.0 - abs(distance - 300.0) / 130.0)
        far_score = max(0.0, (distance - 320.0) / 180.0)
        too_close_score = max(0.0, (160.0 - distance) / 80.0)
        miss_pressure = 0.35

        scores = {
            "Ring": (0.28 + near_score * 1.10 + low_hp * 0.25) * BOSS_GOB_WEIGHTS["Ring"],
            "Spread": (0.42 + mid_score * 0.75 + random.uniform(0.0, 0.12)) * BOSS_GOB_WEIGHTS["Spread"],
            "Spiral": (0.22 + low_hp * 1.00 + miss_pressure * 0.45) * BOSS_GOB_WEIGHTS["Spiral"],
            "Dash": (
                0.28
                + far_score * 0.75
                + too_close_score * 0.60
                + random.uniform(0.0, 0.25)
            ) * BOSS_GOB_WEIGHTS["Dash"],
            "Charge": (
                0.30
                + far_score * 1.10
                + miss_pressure * 0.35
                + low_hp * 0.25
                + random.uniform(0.0, 0.22)
            ) * BOSS_GOB_WEIGHTS["Charge"],
        }
        if self.boss_last_action is not None:
            scores[self.boss_last_action] -= BOSS_GOB_REPEAT_PENALTY
        self.boss_score_snapshot = scores
        choice = max(scores, key=scores.get)
        self.boss_last_action = choice
        return choice

    def _start_boss_action(self, action, player_pos):
        self.boss_action = action
        self.boss_action_timer = 0.0
        self.boss_action_fire_timer = 0.0
        self.boss_action_end_fired = False

        if action == "Ring":
            self.boss_action_duration = 0.35
            self.boss_action_cooldown = 1.05
            self._fire_boss_ring(18, self.bullet_speed, self.damage, 8, (255, 60, 80), 4.0)
        elif action == "Spread":
            self.boss_action_duration = 0.25
            self.boss_action_cooldown = 0.62
            self._fire_boss_spread(player_pos, 7, 13, self.bullet_speed * 1.08, self.damage * 0.72, 7, (255, 130, 60), 3.2)
        elif action == "Spiral":
            self.boss_action_duration = 1.65
            self.boss_action_cooldown = 0.32
        elif action == "Dash":
            self.boss_action_duration = 0.72
            self.boss_action_cooldown = 0.80
            diff = player_pos - self.pos2D
            if diff.length_squared() > 0:
                self.boss_dash_velocity = diff.normalize() * self.speed * 3.2
            else:
                self.boss_dash_velocity = pygame.Vector2(0, 0)
            self._fire_boss_spread(player_pos, 5, 20, self.bullet_speed * 1.15, self.damage * 0.75, 7, (95, 190, 255), 3.0)
        elif action == "Charge":
            self.boss_action_duration = 1.45
            self.boss_action_cooldown = 0.95
            self._reset_boss_charge(player_pos)

    def _run_boss_action(self, delta_time, player_pos, flow_field=None):
        diff = player_pos - self.pos2D
        distance = diff.length()
        direction = diff.normalize() if diff.length_squared() > 0 else pygame.Vector2(1, 0)
        tangent = pygame.Vector2(-direction.y, direction.x) * self.boss_orbit_sign

        if self.boss_action == "Dash":
            self.pos2D += self.boss_dash_velocity * delta_time
            self.boss_dash_velocity *= max(0.0, 1.0 - 3.0 * delta_time)
            if not self.boss_action_end_fired and self.boss_action_timer >= self.boss_action_duration - delta_time:
                self._fire_boss_ring(12, self.bullet_speed * 1.05, self.damage * 0.6, 6, (95, 190, 255), 3.0)
                self.boss_action_end_fired = True
            return

        if self.boss_action == "Charge":
            self._update_boss_charge(delta_time, player_pos)
            return

        if self.boss_action == "Ring":
            self._move_at_boss_pressure_range(player_pos, delta_time, distance, direction, flow_field)
        elif self.boss_action == "Spread":
            self.pos2D += tangent * self.speed * 0.55 * delta_time
            self._move_at_boss_pressure_range(player_pos, delta_time, distance, direction, flow_field)
        elif self.boss_action == "Spiral":
            self.pos2D += tangent * self.speed * 0.65 * delta_time
            self._move_at_boss_pressure_range(player_pos, delta_time, distance, direction, flow_field)
            self.boss_action_fire_timer -= delta_time
            self.boss_spiral_angle += 2.9 * delta_time
            if self.boss_action_fire_timer <= 0:
                for k in range(4):
                    a = self.boss_spiral_angle + k * math.tau / 4.0
                    vel = pygame.Vector2(math.cos(a), math.sin(a)) * self.bullet_speed * 0.88
                    self.enemy_bullets.append(
                        EnemyBullet(self.pos2D, vel, self.damage * 0.6, lifetime=4, radius=7, color=(255, 50, 200))
                    )
                self.boss_action_fire_timer = 0.12

    def _move_at_boss_pressure_range(self, player_pos, delta_time, distance, direction, flow_field=None):
        if distance > 300:
            self._move_towards(player_pos, delta_time, self.speed * 0.9, flow_field)
        elif distance < 165:
            self.pos2D -= direction * self.speed * 0.65 * delta_time
        else:
            self.pos2D += direction * self.speed * 0.25 * delta_time

    def _fire_boss_ring(self, count, speed, damage, radius, color, lifetime):
        offset = random.random() * math.tau
        for i in range(count):
            a = offset + math.tau * i / count
            vel = pygame.Vector2(math.cos(a), math.sin(a)) * speed
            self.enemy_bullets.append(EnemyBullet(self.pos2D, vel, damage, lifetime=lifetime, radius=radius, color=color))

    def _fire_boss_spread(self, player_pos, count, spread_deg, speed, damage, radius, color, lifetime):
        diff = player_pos - self.pos2D
        if diff.length_squared() == 0:
            return
        base_dir = diff.normalize()
        mid = (count - 1) * 0.5
        for i in range(count):
            d = base_dir.rotate((i - mid) * spread_deg)
            self.enemy_bullets.append(EnemyBullet(self.pos2D, d * speed, damage, lifetime=lifetime, radius=radius, color=color))

    def _reset_boss_charge(self, player_pos):
        diff = player_pos - self.pos2D
        if diff.length_squared() > 0:
            self.boss_charge_direction = diff.normalize()
        else:
            self.boss_charge_direction = pygame.Vector2(1, 0)
        self.boss_charge_state = "aim"
        self.boss_charge_timer = 0.55
        self.boss_charge_count = 0

    def _update_boss_charge(self, delta_time, player_pos):
        diff = player_pos - self.pos2D
        if diff.length_squared() > 0:
            target_direction = diff.normalize()
        else:
            target_direction = self.boss_charge_direction

        if self.boss_charge_state == "aim":
            self.boss_charge_direction = target_direction
            self.pos2D += self.boss_charge_direction * self.speed * 0.2 * delta_time
            self.boss_charge_timer -= delta_time
            if self.boss_charge_timer <= 0:
                self.boss_charge_state = "dash"
                self.boss_charge_timer = 0.42
        elif self.boss_charge_state == "dash":
            self.pos2D += self.boss_charge_direction * self.speed * 4.0 * delta_time
            self.boss_charge_timer -= delta_time
            if self.boss_charge_timer <= 0:
                self.boss_charge_count += 1
                if self.boss_charge_count < 2:
                    self.boss_charge_state = "aim"
                    self.boss_charge_timer = 0.38
                else:
                    self.boss_charge_state = "recover"
                    self.boss_charge_timer = 0.65
        elif self.boss_charge_state == "recover":
            self.pos2D += target_direction * self.speed * 0.25 * delta_time
            self.boss_charge_timer -= delta_time
            if self.boss_charge_timer <= 0:
                self.boss_charge_state = "done"
        else:
            self.pos2D += target_direction * self.speed * 0.25 * delta_time

    def draw(self, screen, game):
        screen_pos = game.to_screen(self.pos2D)
        visual_half_height = self.radius
        visual_width = self.radius * 2

        if self.image:
            rect = self.image.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            screen.blit(self.image, rect)
            visual_half_height = rect.height // 2
            visual_width = rect.width
        else:
            pygame.draw.circle(screen, self.color, screen_pos, self.radius)
            pygame.draw.circle(screen, (255, 255, 255), screen_pos, self.radius, 2)

        bar_w = max(60, int(visual_width * 0.7)) if self.is_boss else max(60, int(self.radius * 2.5))
        bar_h = 6
        bar_x = screen_pos.x - bar_w // 2
        bar_y = screen_pos.y - visual_half_height - 15
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (100, 255, 100), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        for b in self.enemy_bullets:
            b.draw(screen, game)

        for dn in self.damage_numbers:
            dn.draw(screen, game)


class EnemyManager:
    def __init__(self, spatial_grid_dict : SpatialGrid):
        self.enemies = []
        self.spawn_timer = 1.0
        self.boss = None
        self.boss_spawned = False
        self.boss_defeated = False
        self.boss_defeat_count = 0
        self.elapsed = 0.0
        self.boss_spawn_time = GAME_CONFIG["boss_spawn_time"]
        self.base_spawn_interval = GAME_CONFIG["spawn_base_interval"]
        self.min_spawn_interval = GAME_CONFIG["spawn_min_interval"]
        self.spawn_ramp_seconds = GAME_CONFIG["spawn_ramp_seconds"]
        self.max_enemies = GAME_CONFIG["max_enemies"]
        self.xp_growth_interval = GAME_CONFIG["xp_drop_growth_interval"]
        self.xp_growth_per_interval = GAME_CONFIG["xp_drop_growth_per_interval"]
        self.xp_drop_max_multiplier = GAME_CONFIG["xp_drop_max_multiplier"]
        self.enemy_hp_growth_per_boss = GAME_CONFIG["enemy_hp_growth_per_boss"]
        self.enemy_damage_growth_per_boss = GAME_CONFIG["enemy_damage_growth_per_boss"]
        self.flow_field = FlowFieldNavigator()

        # for spatial partitioning
        self.spatial_grid_dict = spatial_grid_dict

    def reset(self):
        self.enemies.clear()
        self.spawn_timer = 1.0
        self.boss = None
        self.boss_spawned = False
        self.boss_defeated = False
        self.boss_defeat_count = 0
        self.elapsed = 0.0
        self.flow_field.reset()

    def update(self, delta_time, player_pos, world=None):
        self.elapsed += delta_time

        diff_factor = 1.0 + self.elapsed / self.spawn_ramp_seconds
        spawn_interval = max(self.min_spawn_interval, self.base_spawn_interval / diff_factor)

        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0 and (self.boss is None or not self.boss.alive or len(self.enemies) < self.max_enemies):
            self._spawn_enemy(player_pos)
            self.spawn_timer = spawn_interval

        if not self.boss_spawned and self.elapsed >= self.boss_spawn_time:
            self._spawn_boss(player_pos)

        obstacles = world.obstacles if world is not None else ()
        self.flow_field.update(delta_time, player_pos, obstacles)

        for e in self.enemies[:]:
            e.update(delta_time, player_pos, self.flow_field)
            if self.spatial_grid_dict is not None:
                e.grid_pos = self.spatial_grid_dict.update_entity_pos(e, e.grid_pos, e.pos2D)

            if not e.alive:
                if e.is_boss:
                    self.boss_defeated = True
                    self.boss_defeat_count += 1

                self.spatial_grid_dict.remove_entity(e.grid_pos, e.uuid)

                self.enemies.remove(e)

    def _spawn_enemy(self, player_pos):
        pool = [0, 0, 0]
        if self.elapsed >= 30:
            pool += [1, 1]
        if self.elapsed >= 60:
            pool += [2]
        if self.elapsed >= 90:
            pool += [3, 3]
        enemy_type = random.choice(pool)

        hp_mul, dmg_mul = self._enemy_stat_multipliers()

        angle = random.uniform(0, math.tau)
        dist = random.uniform(700, 900)
        spawn_pos = player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
        new_enemy = Enemy(spawn_pos, enemy_type=enemy_type, hp_mul=hp_mul, dmg_mul=dmg_mul)
        new_enemy.xp_drop = self._scaled_xp_drop(new_enemy.xp_drop)
        self.enemies.append(new_enemy)

        if self.spatial_grid_dict is not None:
            self.spatial_grid_dict.register_entity(new_enemy)

    def _scaled_xp_drop(self, base_drop):
        if self.xp_growth_interval <= 0:
            return base_drop

        growth_tier = int(self.elapsed // self.xp_growth_interval)
        multiplier = 1.0 + growth_tier * self.xp_growth_per_interval
        multiplier = min(multiplier, self.xp_drop_max_multiplier)
        return max(1, int(base_drop * multiplier + 0.5))

    def _enemy_stat_multipliers(self):
        hp_mul = 1.0 + self.boss_defeat_count * self.enemy_hp_growth_per_boss
        dmg_mul = 1.0 + self.boss_defeat_count * self.enemy_damage_growth_per_boss
        return hp_mul, dmg_mul


    def _spawn_boss(self, player_pos):
        self.boss_spawned = True
        angle = random.uniform(0, math.tau)
        spawn_pos = player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * 600
        hp_mul, dmg_mul = self._enemy_stat_multipliers()
        self.boss = Enemy(spawn_pos, hp_mul=hp_mul, dmg_mul=dmg_mul, is_boss=True)
        self.boss.xp_drop = self._scaled_xp_drop(self.boss.xp_drop)
        self.enemies.append(self.boss)

        if self.spatial_grid_dict is not None:
            self.spatial_grid_dict.register_entity(self.boss)

    def all_enemy_bullets(self):
        for e in self.enemies:
            for b in e.enemy_bullets:
                yield b
