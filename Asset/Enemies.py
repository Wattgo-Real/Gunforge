import math
import random

import pygame

<<<<<<< Updated upstream
from Asset.GameSetting import BOSS_CONFIG, ENEMY_CONFIG, GAME_CONFIG

=======
from Asset.GameSetting import BOSS_CONFIG, ENEMY_CONFIG, GAME_CONFIG, GRID_CONFIG 
from Asset.GameSetting import ENTITY_TYPE
from Asset.ImageLoader import load_image_surface
from Asset.SpatialGrid import SpatialGrid
import uuid
>>>>>>> Stashed changes

_ENEMY_IMAGE_CACHE = {}


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
        self.dash_state = "approach"
        self.dash_timer = random.uniform(1.0, 2.5)
        self.boss_phase_timer = 0.0

    def take_damage(self, damage):
        self.hp -= damage
        self.damage_numbers.append(DamageNumber(damage, self.pos2D.copy()))
        if self.hp <= 0:
            self.alive = False

    def _move_towards(self, target_pos, delta_time, speed=None):
        speed = self.speed if speed is None else speed
        diff = target_pos - self.pos2D
        if diff.length_squared() > 0:
            self.pos2D += diff.normalize() * speed * delta_time

    def _move_at_distance(self, target_pos, delta_time, distance):
        diff = target_pos - self.pos2D
        d = diff.length()
        if d == 0:
            return
        direction = diff.normalize()
        if d > distance + 30:
            self.pos2D += direction * self.speed * delta_time
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

    def update(self, delta_time, player_pos):
        self.attack_timer = max(0, self.attack_timer - delta_time)

        if self.ai == "chase":
            self._move_towards(player_pos, delta_time)
        elif self.ai == "runner":
            self.dash_timer -= delta_time
            if self.dash_state == "approach":
                self._move_towards(player_pos, delta_time)
                if self.dash_timer <= 0:
                    self.dash_state = "dash"
                    self.dash_timer = 0.5
            else:
                self._move_towards(player_pos, delta_time, self.speed * 2.4)
                if self.dash_timer <= 0:
                    self.dash_state = "approach"
                    self.dash_timer = random.uniform(1.5, 3.0)
        elif self.ai == "shooter":
            self._move_at_distance(player_pos, delta_time, self.preferred_distance)
            if self.attack_timer <= 0:
                bullet = self._shoot_at(player_pos)
                if bullet:
                    self.enemy_bullets.append(bullet)
                    self.attack_timer = self.attack_cooldown
        elif self.ai == "boss":
            self._update_boss(delta_time, player_pos)

        for b in self.enemy_bullets[:]:
            b.update(delta_time)
            if not b.alive:
                self.enemy_bullets.remove(b)

        for dn in self.damage_numbers[:]:
            dn.update(delta_time)
            if dn.timer <= 0:
                self.damage_numbers.remove(dn)

    def _update_boss(self, delta_time, player_pos):
        self.boss_phase_timer += delta_time
        phase_dur = 5.0
        phase = int(self.boss_phase_timer / phase_dur) % 3

        if phase == 0:
            self._move_towards(player_pos, delta_time, self.speed)
            if self.attack_timer <= 0:
                num = 18
                for i in range(num):
                    a = math.tau * i / num
                    vel = pygame.Vector2(math.cos(a), math.sin(a)) * self.bullet_speed
                    self.enemy_bullets.append(
                        EnemyBullet(self.pos2D, vel, self.damage, lifetime=4, radius=8, color=(255, 60, 80))
                    )
                self.attack_timer = self.attack_cooldown * 1.4
        elif phase == 1:
            self._move_towards(player_pos, delta_time, self.speed * 0.4)
            if self.attack_timer <= 0:
                diff = player_pos - self.pos2D
                if diff.length_squared() > 0:
                    base_dir = diff.normalize()
                    for spread in (-15, -7, 0, 7, 15):
                        d = base_dir.rotate(spread)
                        vel = d * self.bullet_speed
                        self.enemy_bullets.append(
                            EnemyBullet(self.pos2D, vel, self.damage * 0.7, lifetime=3, radius=7, color=(255, 130, 60))
                        )
                self.attack_timer = self.attack_cooldown * 0.6
        else:
            self._move_towards(player_pos, delta_time, self.speed * 0.5)
            if self.attack_timer <= 0:
                base = self.boss_phase_timer * 180
                for k in range(4):
                    a = math.radians(base + k * 90)
                    vel = pygame.Vector2(math.cos(a), math.sin(a)) * self.bullet_speed * 0.85
                    self.enemy_bullets.append(
                        EnemyBullet(self.pos2D, vel, self.damage * 0.6, lifetime=4, radius=7, color=(255, 50, 200))
                    )
                self.attack_timer = 0.15

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
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 1.0
        self.boss = None
        self.boss_spawned = False
        self.boss_defeated = False
        self.elapsed = 0.0
        self.boss_spawn_time = GAME_CONFIG["boss_spawn_time"]
        self.base_spawn_interval = GAME_CONFIG["spawn_base_interval"]
        self.min_spawn_interval = GAME_CONFIG["spawn_min_interval"]

    def reset(self):
        self.enemies.clear()
        self.spawn_timer = 1.0
        self.boss = None
        self.boss_spawned = False
        self.boss_defeated = False
        self.elapsed = 0.0

    def update(self, delta_time, player_pos):
        self.elapsed += delta_time

        diff_factor = 1.0 + self.elapsed / 60.0
        spawn_interval = max(self.min_spawn_interval, self.base_spawn_interval / diff_factor)

        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0 and (self.boss is None or not self.boss.alive or len(self.enemies) < 80):
            self._spawn_enemy(player_pos)
            self.spawn_timer = spawn_interval

        if not self.boss_spawned and self.elapsed >= self.boss_spawn_time:
            self._spawn_boss(player_pos)

        for e in self.enemies[:]:
            e.update(delta_time, player_pos)
            if not e.alive:
                if e.is_boss:
                    self.boss_defeated = True
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

        hp_mul = 1.0 + self.elapsed / 90.0
        dmg_mul = 1.0 + self.elapsed / 180.0

        angle = random.uniform(0, math.tau)
        dist = random.uniform(700, 900)
        spawn_pos = player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
        self.enemies.append(Enemy(spawn_pos, enemy_type=enemy_type, hp_mul=hp_mul, dmg_mul=dmg_mul))

    def _spawn_boss(self, player_pos):
        self.boss_spawned = True
        angle = random.uniform(0, math.tau)
        spawn_pos = player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * 600
        self.boss = Enemy(spawn_pos, is_boss=True)
        self.enemies.append(self.boss)

    def all_enemy_bullets(self):
        for e in self.enemies:
            for b in e.enemy_bullets:
                yield b
