import random
import uuid

import pygame

from Asset.GameSetting import GAME_CONFIG, ENTITY_TYPE, GRID_CONFIG
from Asset.ImageLoader import load_image_surface
from Asset.SpatialGrid import SpatialGrid


_ALTAR_IMAGE_CACHE = {}
_OBSTACLE_SOURCE_CACHE = {}
_OBSTACLE_IMAGE_CACHE = {}
OBSTACLE_SPRITE_HEIGHTS = (170, 210, 250)
OBSTACLE_IMAGE_PATHS = (
    "./Img/obstacle_ruins.png",
    "./Img/obstacle_roots.png",
    "./Img/obstacle_shrine.png",
)


def _get_altar_image(path="./Img/altar_sprite.png", sprite_height=150):
    key = (path, sprite_height)
    if key in _ALTAR_IMAGE_CACHE:
        return _ALTAR_IMAGE_CACHE[key]

    try:
        image = load_image_surface(path)
        width, height = image.get_size()
        scale = sprite_height / height
        image = pygame.transform.smoothscale(image, (max(1, int(width * scale)), int(sprite_height)))
    except (OSError, pygame.error, ValueError):
        image = None

    _ALTAR_IMAGE_CACHE[key] = image
    return image


def _get_obstacle_image(path, sprite_height):
    sprite_height = min(OBSTACLE_SPRITE_HEIGHTS, key=lambda h: abs(h - sprite_height))
    key = (path, sprite_height)
    if key in _OBSTACLE_IMAGE_CACHE:
        return _OBSTACLE_IMAGE_CACHE[key]

    try:
        if path not in _OBSTACLE_SOURCE_CACHE:
            _OBSTACLE_SOURCE_CACHE[path] = load_image_surface(path)

        image = _OBSTACLE_SOURCE_CACHE[path]
        width, height = image.get_size()
        scale = sprite_height / height
        image = pygame.transform.smoothscale(image, (max(1, int(width * scale)), int(sprite_height)))
    except (OSError, pygame.error, ValueError):
        image = None

    _OBSTACLE_IMAGE_CACHE[key] = image
    return image


class XPOrb:
    def __init__(self, position, value=1):
        self.pos2D = pygame.Vector2(position)
        self.value = value
        if value < 3:
            self.radius = 6
            self.color = (100, 255, 100)
        elif value < 15:
            self.radius = 9
            self.color = (100, 200, 255)
        else:
            self.radius = 14
            self.color = (255, 200, 80)
        self.alive = True
        self.attracted = False

    def update(self, delta_time, player_pos):
        pickup_r = GAME_CONFIG["xp_pickup_radius"]
        attract_r = GAME_CONFIG["xp_attract_radius"]
        diff = player_pos - self.pos2D
        d = diff.length()
        if d <= pickup_r:
            self.alive = False
            return True
        if d <= attract_r or self.attracted:
            self.attracted = True
            if d > 0:
                self.pos2D += diff.normalize() * 240 * delta_time
        return False

    def draw(self, screen, game):
        screen_pos = game.to_screen(self.pos2D)
        pygame.draw.circle(screen, self.color, screen_pos, self.radius)
        pygame.draw.circle(screen, (255, 255, 255), screen_pos, self.radius, 1)


class Altar:
    BUFF_TYPES = ("hp", "damage", "speed")

    def __init__(self, position, charge_time=None):
        self.pos2D = pygame.Vector2(position)
        self.radius = 70
        self.charge_time = charge_time if charge_time is not None else GAME_CONFIG["altar_charge_time"]
        self.charge = 0.0
        self.used = False
        self.last_buff = None
        self.image = _get_altar_image()

    def update(self, delta_time, player_pos):
        if self.used:
            return None
        if self.pos2D.distance_to(player_pos) <= self.radius:
            self.charge += delta_time
            if self.charge >= self.charge_time:
                self.used = True
                return True
        else:
            self.charge = max(0.0, self.charge - delta_time * 0.5)
        return None

    def draw(self, screen, game):
        screen_pos = game.to_screen(self.pos2D)
        ratio = min(1.0, self.charge / self.charge_time)

        pygame.draw.circle(screen, (255, 230, 120), screen_pos, self.radius, 2)
        if not self.used and ratio > 0:
            pygame.draw.circle(screen, (255, 230, 120), screen_pos, int(self.radius * ratio), 4)

        if self.image:
            rect = self.image.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            if self.used:
                faded = self.image.copy()
                faded.set_alpha(120)
                screen.blit(faded, rect)
            else:
                screen.blit(self.image, rect)
            return

        if self.used:
            pygame.draw.circle(screen, (60, 60, 60), screen_pos, self.radius, 3)
            pygame.draw.circle(screen, (40, 40, 40), screen_pos, self.radius - 6)
        else:
            pygame.draw.circle(screen, (180, 180, 60), screen_pos, self.radius, 3)
            inner = max(0, int(self.radius * ratio * 0.85))
            if inner > 0:
                pygame.draw.circle(screen, (240, 220, 80), screen_pos, inner)
        pygame.draw.line(screen, (255, 240, 120), (screen_pos.x - 12, screen_pos.y), (screen_pos.x + 12, screen_pos.y), 2)
        pygame.draw.line(screen, (255, 240, 120), (screen_pos.x, screen_pos.y - 12), (screen_pos.x, screen_pos.y + 12), 2)


class Obstacle:
    def __init__(self, position, size, image_path=None, sprite_height=None):
        self.uuid = uuid.uuid4()
        self.entity_type = ENTITY_TYPE["obstacle"]
        self.pos2D = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.color = (90, 90, 100)
        self.registered_cells = []
        self.image_path = image_path if image_path is not None else random.choice(OBSTACLE_IMAGE_PATHS)
        requested_height = int(sprite_height if sprite_height is not None else max(self.size.x, self.size.y))
        self.sprite_height = min(OBSTACLE_SPRITE_HEIGHTS, key=lambda h: abs(h - requested_height))
        self.image = _get_obstacle_image(self.image_path, self.sprite_height)
        self.draw_radius = (self.image.get_width() if self.image else max(self.size.x, self.size.y)) * 0.6

    def add_to_grid(self, spatial_grid_dict : SpatialGrid):
        spatial_grid_dict.register_obstacle(self)

    def remove_from_grid(self, spatial_grid_dict : SpatialGrid):
        spatial_grid_dict.remove_obstacle(self)

    @staticmethod
    def get_nearby_obstacles(pos, spatial_grid_dict : SpatialGrid):
        return spatial_grid_dict.get_entities_near_by_type(pos, ENTITY_TYPE["obstacle"], range_cells=1)

    def _nearest_point(self, point):
        half = self.size / 2
        return pygame.Vector2(
            max(self.pos2D.x - half.x, min(point.x, self.pos2D.x + half.x)),
            max(self.pos2D.y - half.y, min(point.y, self.pos2D.y + half.y)),
        )

    def collides_circle(self, circle_pos, radius):
        nearest = self._nearest_point(circle_pos)
        return (circle_pos - nearest).length() < radius

    def push_out(self, circle_pos, radius):
        nearest = self._nearest_point(circle_pos)
        diff = circle_pos - nearest
        d = diff.length()
        half = self.size / 2
        if d == 0:
            dx = circle_pos.x - self.pos2D.x
            dy = circle_pos.y - self.pos2D.y
            if abs(dx) > abs(dy):
                circle_pos.x = self.pos2D.x + (half.x + radius + 1) * (1 if dx >= 0 else -1)
            else:
                circle_pos.y = self.pos2D.y + (half.y + radius + 1) * (1 if dy >= 0 else -1)
        elif d < radius:
            push = diff.normalize() * (radius - d + 0.5)
            circle_pos += push
        return circle_pos

    def draw(self, screen, game):
        if not self.is_visible(game):
            return

        if self.image:
            screen_pos = game.to_screen(self.pos2D)
            rect = self.image.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            screen.blit(self.image, rect)
            return

        half = self.size / 2
        topleft_world = self.pos2D + pygame.Vector2(-half.x, half.y)
        topleft_screen = game.to_screen(topleft_world)
        rect = pygame.Rect(int(topleft_screen.x), int(topleft_screen.y), int(self.size.x), int(self.size.y))
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (180, 180, 180), rect, 2)

    def is_visible(self, game, margin=160):
        screen_pos = game.to_screen(self.pos2D)
        return (
            -margin <= screen_pos.x <= game.screen_width + margin
            and -margin <= screen_pos.y <= game.screen_height + margin
        )


class WorldChunkManager:
    CHUNK_SIZE = 1000

    def __init__(self, spatial_grid_dict : SpatialGrid = None, seed=42):
        self.spatial_grid_dict = spatial_grid_dict
        self.seed = seed
        self.generated = set()
        self.altars = []
        self.obstacles = []

    def reset(self, seed=None):
        if seed is not None:
            self.seed = seed
        self.generated.clear()
        self.altars.clear()
        self.obstacles.clear()

    def ensure_around(self, player_pos, view_chunks=2):
        cx0 = int(player_pos.x // self.CHUNK_SIZE)
        cy0 = int(player_pos.y // self.CHUNK_SIZE)
        for cx in range(cx0 - view_chunks, cx0 + view_chunks + 1):
            for cy in range(cy0 - view_chunks, cy0 + view_chunks + 1):
                self._generate_chunk(cx, cy)

    def _generate_chunk(self, cx, cy):
        key = (cx, cy)
        if key in self.generated:
            return
        self.generated.add(key)
        rng = random.Random((self.seed * 73856093) ^ (cx * 19349663) ^ (cy * 83492791))

        n_obs = rng.randint(2, 4)
        for _ in range(n_obs):
            x = cx * self.CHUNK_SIZE + rng.uniform(0, self.CHUNK_SIZE)
            y = cy * self.CHUNK_SIZE + rng.uniform(0, self.CHUNK_SIZE)
            sprite_height = rng.choice(OBSTACLE_SPRITE_HEIGHTS)
            w = sprite_height * rng.uniform(0.40, 0.58)
            h = sprite_height * rng.uniform(0.32, 0.46)
            if abs(x) < 220 and abs(y) < 220:
                continue
            obs = Obstacle(
                (x, y),
                (w, h),
                image_path=rng.choice(OBSTACLE_IMAGE_PATHS),
                sprite_height=sprite_height,
            )
            self.obstacles.append(obs)
            if self.spatial_grid_dict is not None:
                obs.add_to_grid(self.spatial_grid_dict)

        if rng.random() < 0.18 and key != (0, 0):
            x = cx * self.CHUNK_SIZE + rng.uniform(150, self.CHUNK_SIZE - 150)
            y = cy * self.CHUNK_SIZE + rng.uniform(150, self.CHUNK_SIZE - 150)
            self.altars.append(Altar((x, y)))

    def cull_far(self, player_pos, max_distance=2500):
        max_sq = max_distance * max_distance
        new_obstacles = []
        for o in self.obstacles:
            if (o.pos2D - player_pos).length_squared() <= max_sq:
                new_obstacles.append(o)
            else:
                if self.spatial_grid_dict is not None:
                    o.remove_from_grid(self.spatial_grid_dict)
        self.obstacles = new_obstacles
        self.altars = [
            a
            for a in self.altars
            if not a.used and (a.pos2D - player_pos).length_squared() <= max_sq
        ]

    def remove_altar(self, altar):
        try:
            self.altars.remove(altar)
        except ValueError:
            pass
