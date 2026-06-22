import math
import random
from collections import deque
from dataclasses import dataclass

import numpy
import pygame

import Asset.Function as GF
from Asset.ImageLoader import load_image_surface


ATTACKS = ("Ring", "Spread", "Spiral", "Dash")
GOB_WEIGHTS = {
    "Ring": 1.05,
    "Spread": 0.82,
    "Spiral": 1.00,
    "Dash": 0.95,
}
GOB_REPEAT_PENALTY = 0.22
ARENA_HALF_SIZE = 620.0
ARENA_DRAW_SIZE = ARENA_HALF_SIZE * 2.0
BOSS_CLOSE_RANGE = 170.0
BOSS_PREFERRED_RANGE = 260.0
BOSS_CHASE_SPEED = 205.0
BOSS_RETREAT_SPEED = 115.0
PLAYER_BULLET_SPEED = 300.0
PLAYER_BULLET_LIFETIME = 0.55
PLAYER_BULLET_RADIUS = 3
PLAYER_BULLET_EFFECTIVE_RANGE = PLAYER_BULLET_SPEED * PLAYER_BULLET_LIFETIME
PLAYER_MODES = ("Behavior", "Scripted")
EVAL2_RUN_TARGET = 30
ATTACK_COLORS = {
    "Ring": (255, 80, 105),
    "Spread": (255, 155, 70),
    "Spiral": (235, 80, 230),
    "Dash": (95, 190, 255),
}
EVAL2_IMAGE_CACHE = {}
PLAYER_SPRITE_PATH = "./Img/player_sprite.png"
PLAYER_SPRITE_BASE_ANGLE = 0
EVAL2_OBSTACLES = (
    (-440, -330, 135, 105, "./Img/obstacle_ruins.png"),
    (410, -285, 115, 145, "./Img/obstacle_roots.png"),
    (-360, 330, 125, 130, "./Img/obstacle_shrine.png"),
    (395, 320, 145, 95, "./Img/obstacle_ruins.png"),
)


def _load_eval_image(path, size=None):
    key = (path, size)
    if key in EVAL2_IMAGE_CACHE:
        return EVAL2_IMAGE_CACHE[key]
    try:
        image = load_image_surface(path)
        if size is not None:
            image = pygame.transform.smoothscale(
                image, (max(1, int(size[0])), max(1, int(size[1])))
            )
    except (OSError, pygame.error, ValueError):
        image = None
    EVAL2_IMAGE_CACHE[key] = image
    return image


def _draw_player_sprite(screen, center, size, direction):
    player_img = _load_eval_image(PLAYER_SPRITE_PATH, (size, size))
    if not player_img:
        pygame.draw.circle(screen, (80, 170, 255), center, max(4, int(size * 0.28)))
        pygame.draw.circle(screen, (235, 250, 255), center, max(4, int(size * 0.22)), 1)
        return

    direction = pygame.Vector2(direction)
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    screen_direction = pygame.Vector2(direction.x, -direction.y)
    angle = -screen_direction.as_polar()[1] + PLAYER_SPRITE_BASE_ANGLE
    rotated = pygame.transform.rotozoom(player_img, angle, 1.0)
    screen.blit(rotated, rotated.get_rect(center=(int(center.x), int(center.y))))


def _scripted_player_position(t):
    return pygame.Vector2(
        math.cos(t * 0.72) * 190.0 + math.sin(t * 1.31) * 45.0,
        math.sin(t * 0.72) * 140.0 + math.cos(t * 1.17) * 40.0,
    )


@dataclass
class EvalBullet:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    damage: float
    color: tuple
    lifetime: float
    owner: str

    def update(self, dt):
        self.pos += self.vel * dt
        self.lifetime -= dt


class BossDecisionEvaluation:
    """Self-contained boss duel used by Evaluation 2.

    All controllers use the same attack pool; only the decision policy differs.
    """

    def __init__(self, title, controller, accent, seed):
        self.title = title
        self.controller = controller
        self.accent = accent
        self.rng = random.Random(seed)
        self.heatmap_bins = 13
        self.heatmap_range = 520.0
        self.heatmap = numpy.zeros((self.heatmap_bins, self.heatmap_bins), dtype=float)

        self.ttk_samples = []
        self.total_elapsed = 0.0
        self.total_boss_damage = 0.0
        self.total_boss_bullets = 0
        self.total_boss_hits = 0
        self.total_phase_switches = 0
        self.total_runs = 0
        self.total_player_losses = 0
        self.total_distance = 0.0
        self.total_distance_samples = 0
        self.survival_samples = []
        self.phase_time_total = {name: 0.0 for name in ATTACKS}

        self.reset_run()

    def reset_all(self):
        self.heatmap.fill(0.0)
        self.ttk_samples.clear()
        self.total_elapsed = 0.0
        self.total_boss_damage = 0.0
        self.total_boss_bullets = 0
        self.total_boss_hits = 0
        self.total_phase_switches = 0
        self.total_runs = 0
        self.total_player_losses = 0
        self.total_distance = 0.0
        self.total_distance_samples = 0
        self.survival_samples.clear()
        self.phase_time_total = {name: 0.0 for name in ATTACKS}
        self.reset_run()

    def reset_run(self):
        self.run_time = 0.0
        self.boss_pos = pygame.Vector2(0, 0)
        self.boss_vel = pygame.Vector2(0, 0)
        self.boss_radius = 36
        self.boss_trace = deque(maxlen=120)
        self.boss_max_hp = 900.0
        self.boss_hp = self.boss_max_hp

        self.player_pos = pygame.Vector2(310, -40)
        self.scripted_prev_pos = self.player_pos.copy()
        self.player_vel = pygame.Vector2(0, 0)
        self.player_radius = 13
        self.player_max_hp = 280.0
        self.player_hp = self.player_max_hp
        self.player_fire_timer = 0.0
        self.player_strafe_sign = 1 if self.rng.random() > 0.5 else -1
        self.player_strafe_timer = 0.0
        self.boss_orbit_sign = 1 if self.rng.random() > 0.5 else -1
        self.camera_pos = self.player_pos.copy()

        self.boss_bullets = []
        self.player_bullets = []
        self.action = None
        self.action_time = 0.0
        self.action_duration = 0.0
        self.action_fire_timer = 0.0
        self.action_end_fired = False
        self.attack_cooldown = 0.25
        self.run_boss_damage = 0.0
        self.run_boss_bullets = 0
        self.run_boss_hits = 0
        self.run_distance = 0.0
        self.run_distance_samples = 0
        self.spiral_angle = self.rng.random() * math.tau
        self.phase_switches = 0
        self.phase_time_run = {name: 0.0 for name in ATTACKS}
        self.fsm_index = -1
        self.gob_last_choice = None
        self.gob_score_snapshot = {name: 0.0 for name in ATTACKS}
        self.boss_trace.append(self.boss_pos.copy())

    def is_complete(self, run_target=EVAL2_RUN_TARGET):
        return run_target is not None and self.total_runs >= run_target

    def update(self, dt, player_mode="Behavior", run_target=EVAL2_RUN_TARGET):
        if self.is_complete(run_target):
            return

        self.run_time += dt
        self.total_elapsed += dt

        if self.action in self.phase_time_run:
            self.phase_time_run[self.action] += dt
            self.phase_time_total[self.action] += dt

        if player_mode == "Scripted":
            self._update_scripted_player(dt)
        else:
            self._update_player_agent(dt)
        self._update_player_fire(dt)
        self._update_boss_controller(dt)
        self._update_bullets(dt)
        self._record_heatmap()
        self._record_distance()
        self._update_camera(dt)
        self.boss_trace.append(self.boss_pos.copy())

        if self.boss_hp <= 0:
            self.ttk_samples.append(self.run_time)
            self.total_runs += 1
            self.reset_run()
        elif self.player_hp <= 0 or self.run_time >= 55.0:
            self.survival_samples.append(self.run_time)
            self.total_runs += 1
            self.total_player_losses += 1
            self.reset_run()

    def _update_scripted_player(self, dt):
        prev = self.player_pos.copy()
        self.player_pos = _scripted_player_position(self.run_time)
        self.player_vel = (self.player_pos - prev) / max(dt, 1e-6)
        self.scripted_prev_pos = prev

    def _update_camera(self, dt):
        target = self.player_pos
        if self.camera_pos.distance_squared_to(target) > 900 * 900:
            self.camera_pos = target.copy()
            return
        follow = min(1.0, dt * 5.0)
        self.camera_pos = self.camera_pos.lerp(target, follow)

    def _update_player_agent(self, dt):
        # Behavior Tree style player:
        # 1. enter bullet range, 2. evade incoming bullets, 3. keep a useful range.
        to_player = self.player_pos - self.boss_pos
        if to_player.length_squared() == 0:
            to_player = pygame.Vector2(1, 0)
        away = to_player.normalize()
        tangent = pygame.Vector2(-away.y, away.x) * self.player_strafe_sign
        distance = to_player.length()
        hittable_distance = PLAYER_BULLET_EFFECTIVE_RANGE + self.boss_radius + PLAYER_BULLET_RADIUS

        self.player_strafe_timer -= dt
        if self.player_strafe_timer <= 0:
            self.player_strafe_sign *= -1
            self.player_strafe_timer = self.rng.uniform(1.2, 2.4)

        if distance > hittable_distance:
            desired = -away * 260.0
        else:
            desired = tangent * 180.0
            if distance < max(115.0, hittable_distance * 0.58):
                desired += away * 240.0
            elif distance > hittable_distance * 0.9:
                desired -= away * 150.0

        if distance <= hittable_distance:
            evade = pygame.Vector2(0, 0)
            for bullet in self.boss_bullets:
                rel = self.player_pos - bullet.pos
                if rel.length_squared() > 150 * 150:
                    continue
                if bullet.vel.length_squared() > 0 and rel.length_squared() > 0:
                    closing = bullet.vel.normalize().dot(rel.normalize())
                    if closing > 0.5:
                        evade += rel.normalize() * (1.1 + closing)
            if evade.length_squared() > 0:
                desired = evade.normalize() * 260.0 + tangent * 80.0

        if distance < 85:
            desired += away * 240.0

        if desired.length() > 240:
            desired.scale_to_length(240)
        steering = desired - self.player_vel
        if steering.length() > 900:
            steering.scale_to_length(900)
        self.player_vel += steering * dt
        if self.player_vel.length() > 260:
            self.player_vel.scale_to_length(260)
        self.player_pos += self.player_vel * dt

    def _update_player_fire(self, dt):
        self.player_fire_timer -= dt
        if self.player_fire_timer > 0:
            return
        direction = self.boss_pos - self.player_pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        direction = direction.normalize()
        self.player_bullets.append(
            EvalBullet(
                self.player_pos.copy(),
                direction * PLAYER_BULLET_SPEED,
                PLAYER_BULLET_RADIUS,
                5.0,
                (150, 225, 255),
                PLAYER_BULLET_LIFETIME,
                "player",
            )
        )
        self.player_fire_timer = 0.10

    def _update_boss_controller(self, dt):
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.action_time += dt

        if self.action is not None:
            self._run_active_action(dt)

        if self.attack_cooldown > 0 or self.action_time < self.action_duration:
            return

        next_action = self._choose_action()
        self._start_action(next_action)

    def _choose_action(self):
        if self.controller == "FSM":
            self.fsm_index = (self.fsm_index + 1) % len(ATTACKS)
            return ATTACKS[self.fsm_index]

        distance = self.player_pos.distance_to(self.boss_pos)
        hp_ratio = self.boss_hp / self.boss_max_hp

        if self.controller == "BT":
            if distance < 210:
                return "Ring"
            if hp_ratio < 0.45 and self.rng.random() < 0.55:
                return "Spiral"
            if distance > 360:
                return "Dash"
            return "Spread"

        # Goal Oriented Behavior / utility AI: weighted utility scores.
        recent_hit_rate = self.total_boss_hits / max(1, self.total_boss_bullets)
        low_hp = 1.0 - hp_ratio
        near_score = max(0.0, (245.0 - distance) / 125.0)
        mid_score = max(0.0, 1.0 - abs(distance - 240.0) / 120.0)
        far_score = max(0.0, (distance - 250.0) / 170.0)
        too_close_score = max(0.0, (170.0 - distance) / 90.0)
        dash_reposition_score = max(0.0, 1.0 - abs(distance - 205.0) / 90.0)
        miss_pressure = max(0.0, (0.16 - recent_hit_rate) / 0.16)

        scores = {
            "Ring": (0.25 + near_score * 1.15 + low_hp * 0.20) * GOB_WEIGHTS["Ring"],
            "Spread": (0.35 + mid_score * 0.85) * GOB_WEIGHTS["Spread"],
            "Spiral": (0.20 + low_hp * 1.10 + miss_pressure * 0.55) * GOB_WEIGHTS["Spiral"],
            "Dash": (
                0.18
                + far_score * 0.75
                + too_close_score * 0.75
                + dash_reposition_score * 0.50
                + self.rng.uniform(0.0, 0.22)
            ) * GOB_WEIGHTS["Dash"],
        }
        if self.gob_last_choice:
            scores[self.gob_last_choice] -= GOB_REPEAT_PENALTY
        self.gob_score_snapshot = scores
        choice = max(scores, key=scores.get)
        self.gob_last_choice = choice
        return choice

    def _start_action(self, action):
        if action != self.action:
            self.phase_switches += 1
            self.total_phase_switches += 1
        self.action = action
        self.action_time = 0.0
        self.action_fire_timer = 0.0
        self.action_end_fired = False

        if action == "Ring":
            self.action_duration = 0.25
            self.attack_cooldown = 0.95
            self._fire_ring(18, 165, 8.0, 7)
        elif action == "Spread":
            self.action_duration = 0.20
            self.attack_cooldown = 0.62
            self._fire_spread(7, 13, 240, 7.0, 6)
        elif action == "Spiral":
            self.action_duration = 1.75
            self.attack_cooldown = 0.35
        elif action == "Dash":
            self.action_duration = 0.72
            self.attack_cooldown = 0.85
            direction = self.player_pos - self.boss_pos
            if direction.length_squared() > 0:
                self.boss_vel = direction.normalize() * 260.0
            self._fire_spread(5, 20, 260, 8.5, 7)

    def _run_active_action(self, dt):
        to_player = self.player_pos - self.boss_pos
        direction = pygame.Vector2(0, 0)
        distance = to_player.length()
        if to_player.length_squared() > 0:
            direction = to_player.normalize()
        tangent = pygame.Vector2(-direction.y, direction.x) * self.boss_orbit_sign

        if self.action == "Dash":
            self.boss_pos += self.boss_vel * dt
            self.boss_vel *= max(0.0, 1.0 - 3.0 * dt)
            if not self.action_end_fired and self.action_time >= self.action_duration - dt:
                self._fire_ring(12, 190, 6.0, 6)
                self.action_end_fired = True
            return

        if self.action == "Ring":
            desired = self._boss_chase_velocity(direction, distance)
            if distance < 210:
                desired = -direction * BOSS_RETREAT_SPEED
            self._steer_boss(desired, dt)
        elif self.action == "Spread":
            desired = tangent * 110.0 + self._boss_chase_velocity(direction, distance)
            self._steer_boss(desired, dt)
        elif self.action == "Spiral":
            desired = tangent * 135.0 + self._boss_chase_velocity(direction, distance)
            self._steer_boss(desired, dt)
            self.action_fire_timer -= dt
            self.spiral_angle += 2.9 * dt
            if self.action_fire_timer <= 0:
                for k in range(4):
                    angle = self.spiral_angle + k * math.tau / 4.0
                    vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * 175.0
                    self._add_boss_bullet(vel, 6.0, 6, ATTACK_COLORS["Spiral"], 4.0)
                self.action_fire_timer = 0.105

    def _boss_chase_velocity(self, direction, distance):
        if distance <= 0:
            return pygame.Vector2(0, 0)
        if distance < BOSS_CLOSE_RANGE:
            return -direction * BOSS_RETREAT_SPEED
        if distance > BOSS_PREFERRED_RANGE:
            chase_scale = min(1.0, (distance - BOSS_PREFERRED_RANGE) / 240.0)
            return direction * (120.0 + (BOSS_CHASE_SPEED - 120.0) * chase_scale)
        return direction * 70.0

    def _steer_boss(self, desired_velocity, dt):
        if desired_velocity.length() > 185:
            desired_velocity.scale_to_length(185)
        steering = desired_velocity - self.boss_vel
        if steering.length() > 520:
            steering.scale_to_length(520)
        self.boss_vel += steering * dt
        if self.boss_vel.length() > 210:
            self.boss_vel.scale_to_length(210)
        self.boss_pos += self.boss_vel * dt
        self.boss_vel *= max(0.0, 1.0 - 0.55 * dt)

    def _fire_ring(self, count, speed, damage, radius):
        offset = self.rng.random() * math.tau
        for idx in range(count):
            angle = offset + math.tau * idx / count
            vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
            self._add_boss_bullet(vel, damage, radius, ATTACK_COLORS["Ring"], 4.2)

    def _fire_spread(self, count, spread_deg, speed, damage, radius):
        direction = self.player_pos - self.boss_pos
        if direction.length_squared() == 0:
            direction = pygame.Vector2(1, 0)
        direction = direction.normalize()
        mid = (count - 1) * 0.5
        for idx in range(count):
            angle = (idx - mid) * spread_deg
            vel = direction.rotate(angle) * speed
            self._add_boss_bullet(vel, damage, radius, ATTACK_COLORS["Spread"], 3.2)

    def _add_boss_bullet(self, vel, damage, radius, color, lifetime):
        self.boss_bullets.append(
            EvalBullet(self.boss_pos.copy(), pygame.Vector2(vel), radius, damage, color, lifetime, "boss")
        )
        self.total_boss_bullets += 1
        self.run_boss_bullets += 1

    def _update_bullets(self, dt):
        for bullet in self.boss_bullets[:]:
            bullet.update(dt)
            if bullet.lifetime <= 0:
                self.boss_bullets.remove(bullet)
                continue
            if bullet.pos.distance_to(self.player_pos) <= bullet.radius + self.player_radius:
                self.total_boss_hits += 1
                self.run_boss_hits += 1
                self.total_boss_damage += bullet.damage
                self.run_boss_damage += bullet.damage
                self.player_hp -= bullet.damage
                self.boss_bullets.remove(bullet)

        for bullet in self.player_bullets[:]:
            bullet.update(dt)
            if bullet.lifetime <= 0:
                self.player_bullets.remove(bullet)
                continue
            if bullet.pos.distance_to(self.boss_pos) <= bullet.radius + self.boss_radius:
                self.boss_hp -= bullet.damage
                self.player_bullets.remove(bullet)

    def _record_heatmap(self):
        rel = self.player_pos - self.boss_pos
        if abs(rel.x) > self.heatmap_range or abs(rel.y) > self.heatmap_range:
            return
        scale = self.heatmap_bins / (self.heatmap_range * 2.0)
        x = int((rel.x + self.heatmap_range) * scale)
        y = int((rel.y + self.heatmap_range) * scale)
        if 0 <= x < self.heatmap_bins and 0 <= y < self.heatmap_bins:
            self.heatmap[y, x] += 1.0

    def _record_distance(self):
        distance = self.player_pos.distance_to(self.boss_pos)
        self.run_distance += distance
        self.run_distance_samples += 1
        self.total_distance += distance
        self.total_distance_samples += 1

    def current_metric_lines(self, run_target=EVAL2_RUN_TARGET):
        current_dps = self.run_boss_damage / max(self.run_time, 1.0)
        current_dodge = 100.0 * (1.0 - self.run_boss_hits / max(1, self.run_boss_bullets))
        avg_distance = self.run_distance / max(1, self.run_distance_samples)
        status = "Complete" if self.is_complete(run_target) else f"Run {self.total_runs + 1}/{run_target}"
        return [
            ("Status", status),
            ("Time / HP", f"{self.run_time:4.1f}s / {self.player_hp:4.0f}"),
            ("Run DPS / dodge", f"{current_dps:4.1f} / {current_dodge:4.0f}%"),
            ("Avg distance", f"{avg_distance:5.0f}"),
        ]

    def aggregate_metric_lines(self):
        ttk = self._ttk_text()
        survival = self._survival_text()
        dps = self.total_boss_damage / max(1.0, self.total_elapsed)
        dodge = 100.0 * (1.0 - self.total_boss_hits / max(1, self.total_boss_bullets))
        avg_distance = self.total_distance / max(1, self.total_distance_samples)
        return [
            ("TTK mean / IQR", ttk),
            ("Survival mean", survival),
            ("Boss DPS", f"{dps:5.1f}"),
            ("Dodge success", f"{dodge:5.1f}%"),
            ("Avg distance", f"{avg_distance:5.0f}"),
        ]

    def _ttk_text(self):
        if not self.ttk_samples:
            return "collecting"
        arr = numpy.array(self.ttk_samples, dtype=float)
        mean = float(arr.mean())
        q1, q3 = numpy.percentile(arr, [25, 75])
        return f"{mean:4.1f}s / {q3 - q1:3.1f}s"

    def _survival_text(self):
        if not self.survival_samples:
            return "none"
        arr = numpy.array(self.survival_samples, dtype=float)
        return f"{float(arr.mean()):4.1f}s"

    def phase_switch_rate(self):
        minutes = max(self.total_elapsed / 60.0, 1.0 / 60.0)
        return self.total_phase_switches / minutes


def _ensure_eval2_state(game):
    if getattr(game, "_eval2_initialized", False) and hasattr(game, "eval2_player_mode_idx"):
        return
    game.eval2_player_mode_idx = 0
    game.eval2_sims = [
        BossDecisionEvaluation("FSM Boss", "FSM", (120, 190, 255), 11),
        BossDecisionEvaluation("Behavior Tree Boss", "BT", (130, 230, 155), 22),
        BossDecisionEvaluation("GOB Boss", "GOB", (255, 190, 95), 33),
    ]
    game._eval2_initialized = True


def _reset_eval2(game):
    _ensure_eval2_state(game)
    for sim in game.eval2_sims:
        sim.reset_all()


def _switch_eval2_player_mode(game):
    _ensure_eval2_state(game)
    game.eval2_player_mode_idx = (game.eval2_player_mode_idx + 1) % len(PLAYER_MODES)
    _reset_eval2(game)


def _world_to_panel(pos, camera, rect, scale):
    rel = (pos - camera) * scale
    return pygame.Vector2(rect.centerx + rel.x, rect.centery - rel.y)


def _draw_scrolling_background(screen, rect, camera, scale):
    source = _load_eval_image("./Img/background.png")
    if not source:
        pygame.draw.rect(screen, (13, 15, 21), rect)
        return

    tile_w, tile_h = source.get_size()
    draw_w = max(1, int(tile_w * scale))
    draw_h = max(1, int(tile_h * scale))
    tile = _load_eval_image("./Img/background.png", (draw_w, draw_h))
    if not tile:
        pygame.draw.rect(screen, (13, 15, 21), rect)
        return

    half_world_w = rect.width / (2.0 * scale)
    half_world_h = rect.height / (2.0 * scale)
    left = camera.x - half_world_w
    right = camera.x + half_world_w
    bottom = camera.y - half_world_h
    top = camera.y + half_world_h

    start_x = math.floor(left / tile_w) * tile_w
    end_x = math.floor(right / tile_w) * tile_w + tile_w
    start_y = math.floor(bottom / tile_h) * tile_h
    end_y = math.floor(top / tile_h) * tile_h + tile_h

    x = start_x
    while x <= end_x:
        y = start_y
        while y <= end_y:
            origin = _world_to_panel(pygame.Vector2(x, y), camera, rect, scale)
            screen.blit(tile, (origin.x, origin.y - draw_h))
            y += tile_h
        x += tile_w


def _draw_heatmap(surface, sim, rect):
    max_value = float(sim.heatmap.max())
    if max_value <= 0:
        return

    size = min(rect.width, rect.height) * 0.72
    cell = size / sim.heatmap_bins
    left = rect.centerx - size / 2
    top = rect.centery - size / 2
    heat = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    for row in range(sim.heatmap_bins):
        for col in range(sim.heatmap_bins):
            value = sim.heatmap[row, col]
            if value <= 0:
                continue
            alpha = min(150, int(25 + 125 * value / max_value))
            color = (255, 95, 60, alpha)
            x = left + col * cell - rect.left
            y = top + row * cell - rect.top
            pygame.draw.rect(heat, color, (x, y, cell + 1, cell + 1))

    surface.blit(heat, rect.topleft)


def _draw_phase_bar(screen, sim, rect, font):
    total = sum(sim.phase_time_total.values())
    bar = pygame.Rect(rect.left + 16, rect.bottom - 56, rect.width - 32, 10)
    pygame.draw.rect(screen, (38, 38, 46), bar)

    x = bar.left
    for phase in ATTACKS:
        ratio = sim.phase_time_total[phase] / total if total > 0 else 0
        width = int(bar.width * ratio)
        if width > 0:
            pygame.draw.rect(screen, ATTACK_COLORS[phase], (x, bar.top, width, bar.height))
        x += width
    pygame.draw.rect(screen, (120, 125, 135), bar, 1)

    switch_text = f"Phase switches/min {sim.phase_switch_rate():.1f}"
    if sim.controller == "GOB":
        switch_text = f"GOB switch freq {sim.phase_switch_rate():.1f}/min"
    label = font.render(switch_text, True, (205, 210, 220))
    screen.blit(label, (bar.left, bar.bottom + 8))


def _draw_panel(game, sim, rect):
    screen = game.screen
    pygame.draw.rect(screen, (19, 21, 28), rect)
    pygame.draw.rect(screen, sim.accent, rect, 2)

    title = game.font.render(sim.title, True, sim.accent)
    screen.blit(title, (rect.left + 16, rect.top + 12))

    subtitle = game.HUD_font.render(
        f"Current phase: {sim.action or 'Starting'}   Boss speed: {sim.boss_vel.length():.0f}",
        True,
        (220, 220, 225),
    )
    screen.blit(subtitle, (rect.left + 16, rect.top + 42))

    metrics_y = rect.top + 70
    section = game.HUD_font.render("Current Run", True, (245, 230, 170))
    screen.blit(section, (rect.left + 16, metrics_y))
    metrics_y += 18
    for label, value in sim.current_metric_lines(EVAL2_RUN_TARGET):
        text = game.HUD_font.render(f"{label}: {value}", True, (235, 235, 235))
        screen.blit(text, (rect.left + 16, metrics_y))
        metrics_y += 17

    metrics_y += 4
    section = game.HUD_font.render("Aggregate", True, (245, 230, 170))
    screen.blit(section, (rect.left + 16, metrics_y))
    metrics_y += 18
    for label, value in sim.aggregate_metric_lines():
        text = game.HUD_font.render(f"{label}: {value}", True, (215, 220, 230))
        screen.blit(text, (rect.left + 16, metrics_y))
        metrics_y += 17

    hp_rect = pygame.Rect(rect.left + 16, metrics_y + 4, rect.width - 32, 10)
    pygame.draw.rect(screen, (55, 25, 32), hp_rect)
    hp_ratio = max(0.0, sim.boss_hp / sim.boss_max_hp)
    pygame.draw.rect(screen, (220, 70, 90), (hp_rect.left, hp_rect.top, int(hp_rect.width * hp_ratio), hp_rect.height))
    pygame.draw.rect(screen, (130, 130, 140), hp_rect, 1)

    play_area_top = max(rect.top + 142, metrics_y + 22)
    play_area_h = max(80, rect.bottom - play_area_top - 72)
    play_area = pygame.Rect(rect.left + 12, play_area_top, rect.width - 24, play_area_h)
    old_clip = screen.get_clip()
    screen.set_clip(play_area)
    scale = min(play_area.width, play_area.height) / ARENA_DRAW_SIZE
    camera = sim.camera_pos
    _draw_scrolling_background(screen, play_area, camera, scale)
    _draw_heatmap(screen, sim, play_area)

    for ox, oy, ow, oh, path in EVAL2_OBSTACLES:
        center = _world_to_panel(pygame.Vector2(ox, oy), camera, play_area, scale)
        obstacle = _load_eval_image(path, (ow * scale, oh * scale))
        if obstacle:
            screen.blit(obstacle, obstacle.get_rect(center=center))
        else:
            fallback = pygame.Rect(0, 0, int(ow * scale), int(oh * scale))
            fallback.center = center
            pygame.draw.rect(screen, (75, 70, 86), fallback)

    for radius in (160, 320, 480):
        center = _world_to_panel(sim.boss_pos, camera, play_area, scale)
        pygame.draw.circle(screen, (42, 46, 56), center, int(radius * scale), 1)

    if len(sim.boss_trace) >= 2:
        trace_points = [_world_to_panel(pos, camera, play_area, scale) for pos in sim.boss_trace]
        pygame.draw.lines(screen, (255, 235, 150), False, trace_points, 2)

    for bullet in sim.boss_bullets:
        pos = _world_to_panel(bullet.pos, camera, play_area, scale)
        pygame.draw.circle(screen, bullet.color, pos, max(2, int(bullet.radius * scale)))
    for bullet in sim.player_bullets:
        pos = _world_to_panel(bullet.pos, camera, play_area, scale)
        pygame.draw.circle(screen, bullet.color, pos, max(2, int(bullet.radius * scale)))

    boss_screen = _world_to_panel(sim.boss_pos, camera, play_area, scale)
    player_screen = _world_to_panel(sim.player_pos, camera, play_area, scale)
    boss_size = max(32, int(sim.boss_radius * 3.1 * scale))
    boss_img = _load_eval_image("./Img/boss_sprite.png", (boss_size, boss_size))
    if boss_img:
        screen.blit(boss_img, boss_img.get_rect(center=boss_screen))
    else:
        pygame.draw.circle(screen, (105, 70, 82), boss_screen, int(sim.boss_radius * scale + 5))
        pygame.draw.circle(screen, sim.accent, boss_screen, int(sim.boss_radius * scale))
        pygame.draw.circle(screen, (255, 255, 255), boss_screen, int(sim.boss_radius * scale), 2)

    player_size = max(24, int(sim.player_radius * 6.2 * scale))
    player_direction = sim.boss_pos - sim.player_pos
    if player_direction.length_squared() == 0:
        player_direction = sim.player_vel
    _draw_player_sprite(screen, player_screen, player_size, player_direction)
    pygame.draw.line(screen, (90, 120, 150), boss_screen, player_screen, 1)
    screen.set_clip(old_clip)
    pygame.draw.rect(screen, (48, 52, 64), play_area, 1)

    _draw_phase_bar(screen, sim, rect, game.HUD_font)


def test_screen_eval2(game, events):
    _ensure_eval2_state(game)

    back_btn = pygame.Rect(game.screen_width - 150, 18, 120, 42)
    reset_btn = pygame.Rect(game.screen_width - 290, 18, 120, 42)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.test_screen = 4
                return
            if event.key == pygame.K_r:
                _reset_eval2(game)
            elif event.key == pygame.K_t:
                _switch_eval2_player_mode(game)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn.collidepoint(event.pos):
                game.test_screen = 4
                return
            if reset_btn.collidepoint(event.pos):
                _reset_eval2(game)

    player_mode = PLAYER_MODES[game.eval2_player_mode_idx]
    for sim in game.eval2_sims:
        sim.update(game.delta_time, player_mode, EVAL2_RUN_TARGET)

    game.screen.fill((15, 16, 22))
    title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 34, bold=True)
    title = title_font.render("Evaluation 2 - Boss Decision Systems", True, (245, 245, 245))
    game.screen.blit(title, (28, 18))
    complete = all(sim.is_complete(EVAL2_RUN_TARGET) for sim in game.eval2_sims)
    state = "Complete" if complete else "Running"
    hint = game.HUD_font.render(
        f"{state} | Player mode: {player_mode} | Target {EVAL2_RUN_TARGET} runs. "
        "T toggles player, R resets samples.",
        True,
        (180, 185, 195),
    )
    game.screen.blit(hint, (30, 54))

    GF.draw_button(game.screen, reset_btn, "Reset", font=game.HUD_font, color=(80, 95, 130))
    GF.draw_button(game.screen, back_btn, "Back", font=game.HUD_font, color=(80, 95, 130))

    margin = 22
    top = 92
    gap = 14
    panel_w = (game.screen_width - margin * 2 - gap * 2) // 3
    panel_h = game.screen_height - top - 24
    for idx, sim in enumerate(game.eval2_sims):
        rect = pygame.Rect(margin + idx * (panel_w + gap), top, panel_w, panel_h)
        _draw_panel(game, sim, rect)
