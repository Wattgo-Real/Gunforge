import heapq
import math
import random
import time
from collections import deque

import pygame

import Asset.Function as GF
from Asset.GameSetting import GAME_CONFIG
from Asset.ImageLoader import load_image_surface
from Asset.Pickups import WorldChunkManager


METHODS = ("Steering", "A*", "Dijkstra", "Flow Field")
N_VALUES = (10, 30, 60, 120, 200, 300)
DT = 1.0 / 60.0
CELL_SIZE = GAME_CONFIG["flow_field_cell_size"]
RADIUS_CELLS = GAME_CONFIG["flow_field_radius_cells"]
GRID_W = RADIUS_CELLS * 2 + 1
GRID_H = RADIUS_CELLS * 2 + 1
VIEW_W = GRID_W * CELL_SIZE
VIEW_H = GRID_H * CELL_SIZE
OBSTACLE_PADDING = GAME_CONFIG["flow_field_obstacle_padding"]
ENEMY_SPEED = 92.0
FRAME_BUDGET_MS = 16.0
SUMMARY_FRAME_TARGET = 900

METHOD_COLORS = {
    "Steering": (245, 175, 90),
    "A*": (115, 190, 255),
    "Dijkstra": (155, 230, 145),
    "Flow Field": (235, 135, 245),
}
EVAL1_IMAGE_CACHE = {}
PLAYER_SPRITE_PATH = "./Img/player_sprite.png"
PLAYER_SPRITE_BASE_ANGLE = 0
OBSTACLE_IMAGE_PATHS = (
    "./Img/obstacle_ruins.png",
    "./Img/obstacle_roots.png",
    "./Img/obstacle_shrine.png",
)


def _load_eval_image(path, size=None):
    key = (path, size)
    if key in EVAL1_IMAGE_CACHE:
        return EVAL1_IMAGE_CACHE[key]
    try:
        image = load_image_surface(path)
        if size is not None:
            image = pygame.transform.smoothscale(
                image, (max(1, int(size[0])), max(1, int(size[1])))
            )
    except (OSError, pygame.error, ValueError):
        image = None
    EVAL1_IMAGE_CACHE[key] = image
    return image


def _draw_player_sprite(screen, center, size, direction):
    player_img = _load_eval_image(PLAYER_SPRITE_PATH, (size, size))
    if not player_img:
        pygame.draw.circle(screen, (80, 185, 255), center, max(4, int(size * 0.3)))
        pygame.draw.circle(screen, (235, 250, 255), center, max(4, int(size * 0.3)), 1)
        return

    direction = pygame.Vector2(direction)
    if direction.length_squared() == 0:
        direction = pygame.Vector2(1, 0)
    screen_direction = pygame.Vector2(direction.x, -direction.y)
    angle = -screen_direction.as_polar()[1] + PLAYER_SPRITE_BASE_ANGLE
    rotated = pygame.transform.rotozoom(player_img, angle, 1.0)
    screen.blit(rotated, rotated.get_rect(center=(int(center.x), int(center.y))))


NEIGHBORS_4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
NEIGHBORS_8 = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
)


def _world_to_cell(pos):
    return (
        math.floor(pos.x / CELL_SIZE),
        math.floor(pos.y / CELL_SIZE),
    )


def _to_local(world_cell, origin_cell):
    return (
        world_cell[0] - origin_cell[0],
        world_cell[1] - origin_cell[1],
    )


def _to_world_cell(local_cell, origin_cell):
    return (
        local_cell[0] + origin_cell[0],
        local_cell[1] + origin_cell[1],
    )


def _cell_to_world(local_cell, origin_cell):
    world_cell = _to_world_cell(local_cell, origin_cell)
    return pygame.Vector2(
        (world_cell[0] + 0.5) * CELL_SIZE,
        (world_cell[1] + 0.5) * CELL_SIZE,
    )


def _in_bounds(cell):
    x, y = cell
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def _is_walkable(cell, blocked):
    return _in_bounds(cell) and cell not in blocked


def _blocked_cells(obstacles, origin_cell):
    blocked = set()
    for obs in obstacles:
        half = obs.size / 2
        min_cell = _world_to_cell(
            pygame.Vector2(
                obs.pos2D.x - half.x - OBSTACLE_PADDING,
                obs.pos2D.y - half.y - OBSTACLE_PADDING,
            )
        )
        max_cell = _world_to_cell(
            pygame.Vector2(
                obs.pos2D.x + half.x + OBSTACLE_PADDING,
                obs.pos2D.y + half.y + OBSTACLE_PADDING,
            )
        )
        min_local = _to_local(min_cell, origin_cell)
        max_local = _to_local(max_cell, origin_cell)
        for lx in range(max(0, min_local[0]), min(GRID_W, max_local[0] + 1)):
            for ly in range(max(0, min_local[1]), min(GRID_H, max_local[1] + 1)):
                blocked.add((lx, ly))
    return blocked


def _nearest_walkable(cell, blocked):
    if _is_walkable(cell, blocked):
        return cell
    queue = [cell]
    seen = {cell}
    while queue:
        curr = queue.pop(0)
        for dx, dy in NEIGHBORS_4:
            nxt = (curr[0] + dx, curr[1] + dy)
            if nxt in seen:
                continue
            if _is_walkable(nxt, blocked):
                return nxt
            if _in_bounds(nxt):
                seen.add(nxt)
                queue.append(nxt)
    return (RADIUS_CELLS, RADIUS_CELLS)


def _heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _edge_cost(a, b):
    return math.sqrt(2.0) if a[0] != b[0] and a[1] != b[1] else 1.0


def _reconstruct(came_from, start, goal):
    if goal not in came_from and goal != start:
        return []
    path = [goal]
    curr = goal
    while curr != start:
        curr = came_from[curr]
        path.append(curr)
    path.reverse()
    return path


def _search_path(start, goal, blocked, use_heuristic):
    start = _nearest_walkable(start, blocked)
    goal = _nearest_walkable(goal, blocked)
    frontier = [(0.0, start)]
    came_from = {}
    cost_so_far = {start: 0.0}
    expanded = 0

    while frontier:
        _, curr = heapq.heappop(frontier)
        expanded += 1
        if curr == goal:
            break

        for dx, dy in NEIGHBORS_8:
            nxt = (curr[0] + dx, curr[1] + dy)
            if not _is_walkable(nxt, blocked):
                continue
            if dx != 0 and dy != 0:
                if not _is_walkable((curr[0] + dx, curr[1]), blocked):
                    continue
                if not _is_walkable((curr[0], curr[1] + dy), blocked):
                    continue
            new_cost = cost_so_far[curr] + _edge_cost(curr, nxt)
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + (_heuristic(nxt, goal) if use_heuristic else 0.0)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = curr

    return _reconstruct(came_from, start, goal), cost_so_far.get(goal), expanded


def _build_flow_field(goal, blocked):
    goal = _nearest_walkable(goal, blocked)
    frontier = [(0.0, goal)]
    dist = {goal: 0.0}
    expanded = 0

    while frontier:
        curr_cost, curr = heapq.heappop(frontier)
        if curr_cost > dist[curr]:
            continue
        expanded += 1
        for dx, dy in NEIGHBORS_8:
            nxt = (curr[0] + dx, curr[1] + dy)
            if not _is_walkable(nxt, blocked):
                continue
            if dx != 0 and dy != 0:
                if not _is_walkable((curr[0] + dx, curr[1]), blocked):
                    continue
                if not _is_walkable((curr[0], curr[1] + dy), blocked):
                    continue
            new_cost = curr_cost + _edge_cost(curr, nxt)
            if nxt not in dist or new_cost < dist[nxt]:
                dist[nxt] = new_cost
                heapq.heappush(frontier, (new_cost, nxt))

    flow = {}
    for cell, cell_cost in dist.items():
        if cell == goal:
            continue
        best = None
        best_cost = cell_cost
        for dx, dy in NEIGHBORS_8:
            nxt = (cell[0] + dx, cell[1] + dy)
            if nxt in dist and dist[nxt] < best_cost:
                best = nxt
                best_cost = dist[nxt]
        if best is not None:
            direction = pygame.Vector2(best[0] - cell[0], best[1] - cell[1])
            if direction.length_squared() > 0:
                flow[cell] = direction.normalize()
    return dist, flow, expanded


def _scripted_player(frame):
    t = frame / 60.0
    return pygame.Vector2(
        t * 155.0 + math.sin(t * 0.9) * 360 + math.sin(t * 1.7) * 120,
        t * 95.0 + math.cos(t * 0.7) * 250,
    )


def _position_is_free(pos, origin_cell, blocked):
    local = _to_local(_world_to_cell(pos), origin_cell)
    return not (_in_bounds(local) and local in blocked)


def _spawn_enemy_from_rng(rng, player_pos, origin_cell, blocked):
    for _ in range(80):
        angle = rng.uniform(0, math.tau)
        dist = rng.uniform(700, 900)
        pos = player_pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * dist
        if not _position_is_free(pos, origin_cell, blocked):
            continue
        return {
            "pos": pos,
            "start": pos.copy(),
            "path": [],
            "path_idx": 0,
            "stuck_time": 0.0,
            "stuck_counted": False,
            "path_len": 0.0,
        }
    pos = player_pos + pygame.Vector2(820, 0)
    return {
        "pos": pos,
        "start": pos.copy(),
        "path": [],
        "path_idx": 0,
        "stuck_time": 0.0,
        "stuck_counted": False,
        "path_len": 0.0,
    }


def _spawn_enemies(count, rng, player_pos, origin_cell, blocked):
    return [_spawn_enemy_from_rng(rng, player_pos, origin_cell, blocked) for _ in range(count)]


def _near_obstacle(cell, blocked):
    for dx, dy in NEIGHBORS_8:
        if (cell[0] + dx, cell[1] + dy) in blocked:
            return True
    return False


def _line_crosses_obstacle(start_pos, end_pos, origin_cell, blocked):
    distance = max(1.0, start_pos.distance_to(end_pos))
    steps = max(2, int(distance / (CELL_SIZE * 0.5)))
    for i in range(1, steps + 1):
        pos = start_pos.lerp(end_pos, i / steps)
        local = _to_local(_world_to_cell(pos), origin_cell)
        if _in_bounds(local) and local in blocked:
            return True
    return False


def _try_move(pos, velocity, origin_cell, blocked):
    next_pos = pos + velocity
    if _position_is_free(next_pos, origin_cell, blocked):
        return next_pos

    slide_x = pygame.Vector2(pos.x + velocity.x, pos.y)
    if _position_is_free(slide_x, origin_cell, blocked):
        return slide_x

    slide_y = pygame.Vector2(pos.x, pos.y + velocity.y)
    if _position_is_free(slide_y, origin_cell, blocked):
        return slide_y

    return pos


class LivePathEvaluation:
    def __init__(self, method, enemy_count):
        self.method = method
        self.enemy_count = enemy_count
        self.rng = random.Random(9000 + enemy_count * 13 + METHODS.index(method))
        self.player_trace = deque(maxlen=180)
        self.world = WorldChunkManager(spatial_grid_dict=None, seed=42)
        self.origin_cell = (0, 0)
        self.blocked = set()
        self.reset(enemy_count)

    def _refresh_world(self, player_pos):
        self.world.ensure_around(player_pos, view_chunks=2)
        self.world.cull_far(player_pos, max_distance=2500)
        player_cell = _world_to_cell(player_pos)
        self.origin_cell = (
            player_cell[0] - RADIUS_CELLS,
            player_cell[1] - RADIUS_CELLS,
        )
        self.blocked = _blocked_cells(self.world.obstacles, self.origin_cell)
        return player_cell, _to_local(player_cell, self.origin_cell)

    def reset(self, enemy_count=None):
        if enemy_count is not None:
            self.enemy_count = enemy_count
        self.frame = 0
        self.world.reset(seed=42)
        initial_player = _scripted_player(self.frame)
        self.player_cell, self.player_local = self._refresh_world(initial_player)
        self.enemies = _spawn_enemies(
            self.enemy_count,
            self.rng,
            initial_player,
            self.origin_cell,
            self.blocked,
        )
        self.flow_dist = {}
        self.flow = {}
        self.flow_goal = None
        self.flow_timer = 0.0
        self.recomputes = 0
        self.expanded_this_frame = 0
        self.reached = 0
        self.path_ms_ema = 0.0
        self.total_ms_ema = 0.0
        self.detour_ema = 1.0
        self.stuck_count = 0
        self.summary_printed = False
        self.player_trace.clear()

    def update(self):
        t_total = time.perf_counter()
        self.frame += 1
        self.expanded_this_frame = 0
        path_ms = 0.0
        detour_values = []

        player_pos = _scripted_player(self.frame)
        player_world_cell, player_cell = self._refresh_world(player_pos)
        player_cell = _nearest_walkable(player_cell, self.blocked)
        self.player_trace.append(player_pos.copy())

        self.flow_timer -= DT
        if (
            self.method == "Flow Field"
            and (
                self.flow_goal != player_world_cell
                or self.flow_timer <= 0
                or not self.flow
            )
        ):
            t0 = time.perf_counter()
            self.flow_dist, self.flow, expanded = _build_flow_field(player_cell, self.blocked)
            path_ms += (time.perf_counter() - t0) * 1000.0
            self.expanded_this_frame += expanded
            self.flow_goal = player_world_cell
            self.flow_timer = GAME_CONFIG["flow_field_refresh_interval"]
            self.recomputes += 1

        for idx, enemy in enumerate(self.enemies):
            pos = enemy["pos"]
            start_world_cell = _world_to_cell(pos)
            start_cell = _nearest_walkable(_to_local(start_world_cell, self.origin_cell), self.blocked)
            direction = pygame.Vector2(0, 0)

            if self.method == "Steering":
                target = player_pos
                direction = target - pos
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                detour_values.append(
                    1.65 if _line_crosses_obstacle(pos, player_pos, self.origin_cell, self.blocked) else 1.0
                )

            elif self.method in ("A*", "Dijkstra"):
                needs_path = True
                if needs_path:
                    t0 = time.perf_counter()
                    path, cost, expanded = _search_path(
                        start_cell,
                        player_cell,
                        self.blocked,
                        self.method == "A*",
                    )
                    path_ms += (time.perf_counter() - t0) * 1000.0
                    self.expanded_this_frame += expanded
                    enemy["path"] = path
                    enemy["path_idx"] = 1 if len(path) > 1 else 0
                    if cost is not None and cost > 0:
                        start_center = _cell_to_world(start_cell, self.origin_cell)
                        goal_center = _cell_to_world(player_cell, self.origin_cell)
                        euclid = max(1.0, start_center.distance_to(goal_center))
                        detour_values.append((cost * CELL_SIZE) / euclid)

                if enemy["path"] and enemy["path_idx"] < len(enemy["path"]):
                    target = _cell_to_world(enemy["path"][enemy["path_idx"]], self.origin_cell)
                    if pos.distance_to(target) < CELL_SIZE * 0.35:
                        enemy["path_idx"] += 1
                else:
                    target = player_pos

                direction = target - pos
                if direction.length_squared() > 0:
                    direction = direction.normalize()

            else:
                direction = self.flow.get(start_cell, pygame.Vector2(0, 0))
                if start_cell in self.flow_dist and self.flow_dist[start_cell] > 0:
                    start_center = _cell_to_world(start_cell, self.origin_cell)
                    goal_center = _cell_to_world(player_cell, self.origin_cell)
                    euclid = max(1.0, start_center.distance_to(goal_center))
                    detour_values.append((self.flow_dist[start_cell] * CELL_SIZE) / euclid)

            old_pos = pos.copy()
            new_pos = _try_move(pos, direction * ENEMY_SPEED * DT, self.origin_cell, self.blocked)
            moved = old_pos.distance_to(new_pos)
            enemy["pos"] = new_pos
            enemy["path_len"] += moved

            new_cell = _to_local(_world_to_cell(new_pos), self.origin_cell)
            if _near_obstacle(new_cell, self.blocked) and moved < ENEMY_SPEED * DT * 0.35:
                enemy["stuck_time"] += DT
                if enemy["stuck_time"] > 2.0 and not enemy["stuck_counted"]:
                    enemy["stuck_counted"] = True
            else:
                enemy["stuck_time"] = 0.0

            if new_pos.distance_to(player_pos) < 22:
                self.reached += 1
                self.enemies[idx] = _spawn_enemy_from_rng(
                    self.rng,
                    player_pos,
                    self.origin_cell,
                    self.blocked,
                )

        total_ms = (time.perf_counter() - t_total) * 1000.0
        alpha = 0.08
        self.path_ms_ema = (1 - alpha) * self.path_ms_ema + alpha * path_ms
        self.total_ms_ema = (1 - alpha) * self.total_ms_ema + alpha * total_ms
        if detour_values:
            detour = sum(detour_values) / len(detour_values)
            self.detour_ema = (1 - alpha) * self.detour_ema + alpha * detour
        self.stuck_count = sum(1 for enemy in self.enemies if enemy["stuck_counted"])

    def recomputes_per_min(self):
        sim_minutes = max((self.frame * DT) / 60.0, 1.0 / 60.0)
        return self.recomputes / sim_minutes

    def print_summary_if_ready(self):
        if self.summary_printed or self.frame < SUMMARY_FRAME_TARGET:
            return
        self.summary_printed = True
        print(
            "[EVAL1_RESULT] "
            f"method={self.method} "
            f"N={self.enemy_count} "
            f"frames={self.frame} "
            f"frame_ms={self.total_ms_ema:.3f} "
            f"nav_ms={self.path_ms_ema:.3f} "
            f"detour={self.detour_ema:.3f} "
            f"stuck={self.stuck_count} "
            f"reached={self.reached} "
            f"expanded={self.expanded_this_frame} "
            f"recomputes_per_min={self.recomputes_per_min():.2f}"
        )


def _ensure_eval1_state(game):
    if getattr(game, "_eval1_initialized", False) and hasattr(game, "eval1_sim"):
        return
    game.eval1_enemy_idx = 1
    game.eval1_method_idx = 0
    game.eval1_paused = False
    enemy_count = N_VALUES[game.eval1_enemy_idx]
    method = METHODS[game.eval1_method_idx]
    game.eval1_sim = LivePathEvaluation(method, enemy_count)
    game._eval1_initialized = True


def _reset_eval1(game):
    _ensure_eval1_state(game)
    enemy_count = N_VALUES[game.eval1_enemy_idx]
    method = METHODS[game.eval1_method_idx]
    game.eval1_sim = LivePathEvaluation(method, enemy_count)


def _switch_eval1_method(game, step):
    _ensure_eval1_state(game)
    game.eval1_method_idx = (game.eval1_method_idx + step) % len(METHODS)
    _reset_eval1(game)


def _switch_eval1_enemy_count(game, step):
    _ensure_eval1_state(game)
    game.eval1_enemy_idx = (game.eval1_enemy_idx + step) % len(N_VALUES)
    _reset_eval1(game)


def _draw_text(game, text, x, y, color=(230, 230, 230), font=None):
    surf = (font or game.HUD_font).render(text, True, color)
    game.screen.blit(surf, (x, y))
    return surf.get_height()


def _world_to_rect(pos, area, sim):
    scale = min(area.width / VIEW_W, area.height / VIEW_H)
    draw_w = VIEW_W * scale
    draw_h = VIEW_H * scale
    left = area.left + (area.width - draw_w) * 0.5
    top = area.top + (area.height - draw_h) * 0.5
    player_pos = _scripted_player(sim.frame)
    view_left = player_pos.x - VIEW_W * 0.5
    view_top = player_pos.y - VIEW_H * 0.5
    return pygame.Vector2(
        left + (pos.x - view_left) * scale,
        top + (pos.y - view_top) * scale,
    ), scale, left, top


def _draw_world_background(screen, map_rect, scale, sim):
    background = _load_eval_image("./Img/background.png")
    if not background:
        pygame.draw.rect(screen, (14, 17, 24), map_rect)
        return

    player_pos = _scripted_player(sim.frame)
    view_left = player_pos.x - VIEW_W * 0.5
    view_top = player_pos.y - VIEW_H * 0.5
    tile_world = WorldChunkManager.CHUNK_SIZE
    tile_px = max(1, int(tile_world * scale))
    tile = _load_eval_image("./Img/background.png", (tile_px, tile_px))
    if not tile:
        pygame.draw.rect(screen, (14, 17, 24), map_rect)
        return

    start_x = math.floor(view_left / tile_world) * tile_world
    start_y = math.floor(view_top / tile_world) * tile_world
    end_x = view_left + VIEW_W
    end_y = view_top + VIEW_H

    old_clip = screen.get_clip()
    screen.set_clip(map_rect)
    wx = start_x
    while wx < end_x:
        wy = start_y
        while wy < end_y:
            sx = map_rect.left + int((wx - view_left) * scale)
            sy = map_rect.top + int((wy - view_top) * scale)
            screen.blit(tile, (sx, sy))
            wy += tile_world
        wx += tile_world

    grid_color = (38, 45, 55)
    wx = start_x
    while wx <= end_x:
        sx = map_rect.left + int((wx - view_left) * scale)
        pygame.draw.line(screen, grid_color, (sx, map_rect.top), (sx, map_rect.bottom), 1)
        wx += tile_world
    wy = start_y
    while wy <= end_y:
        sy = map_rect.top + int((wy - view_top) * scale)
        pygame.draw.line(screen, grid_color, (map_rect.left, sy), (map_rect.right, sy), 1)
        wy += tile_world
    screen.set_clip(old_clip)


def _draw_obstacles(screen, area, sim):
    _, scale, left, top = _world_to_rect(_scripted_player(sim.frame), area, sim)
    map_rect = pygame.Rect(left, top, VIEW_W * scale, VIEW_H * scale)
    _draw_world_background(screen, map_rect, scale, sim)
    pygame.draw.rect(screen, (58, 64, 78), map_rect, 1)

    player_pos = _scripted_player(sim.frame)
    view_rect = pygame.Rect(
        player_pos.x - VIEW_W * 0.5,
        player_pos.y - VIEW_H * 0.5,
        VIEW_W,
        VIEW_H,
    )
    for obs in sim.world.obstacles:
        half = obs.size / 2
        obs_rect = pygame.Rect(obs.pos2D.x - half.x, obs.pos2D.y - half.y, obs.size.x, obs.size.y)
        if not view_rect.colliderect(obs_rect):
            continue
        center, _, _, _ = _world_to_rect(obs.pos2D, area, sim)
        rect = pygame.Rect(0, 0, obs.size.x * scale, obs.size.y * scale)
        rect.center = center
        obstacle = _load_eval_image(obs.image_path, (rect.width * 1.45, rect.height * 1.65))
        if obstacle:
            image_rect = obstacle.get_rect(center=rect.center)
            screen.blit(obstacle, image_rect)
        else:
            pygame.draw.rect(screen, (83, 70, 96), rect)

    return scale, left, top, map_rect


def _draw_flow_arrows(screen, sim, area):
    if not sim.flow:
        return
    for cell, direction in sim.flow.items():
        if cell[0] % 4 != 0 or cell[1] % 4 != 0:
            continue
        start, scale, _, _ = _world_to_rect(_cell_to_world(cell, sim.origin_cell), area, sim)
        end = start + pygame.Vector2(direction.x, -direction.y) * CELL_SIZE * scale * 0.55
        pygame.draw.line(screen, (210, 130, 230), start, end, 1)


def _draw_paths(screen, sim, area):
    if sim.method not in ("A*", "Dijkstra"):
        return
    color = METHOD_COLORS[sim.method]
    drawn = 0
    for enemy in sim.enemies:
        if len(enemy["path"]) < 2:
            continue
        points = [
            _world_to_rect(_cell_to_world(cell, sim.origin_cell), area, sim)[0]
            for cell in enemy["path"]
        ]
        if len(points) >= 2:
            pygame.draw.lines(screen, color, False, points, 1)
            drawn += 1
        if drawn >= 10:
            break


def _draw_steering_rays(screen, sim, player_pos, area):
    if sim.method != "Steering":
        return
    for enemy in sim.enemies[:10]:
        start = _world_to_rect(enemy["pos"], area, sim)[0]
        end = _world_to_rect(player_pos, area, sim)[0]
        pygame.draw.line(screen, (190, 125, 80), start, end, 1)


def _draw_panel(game, sim, rect):
    color = METHOD_COLORS[sim.method]
    pygame.draw.rect(game.screen, (19, 22, 30), rect)
    pygame.draw.rect(game.screen, color, rect, 2)

    _draw_text(game, sim.method, rect.left + 14, rect.top + 10, color, game.font)
    budget_color = (130, 245, 155) if sim.total_ms_ema <= FRAME_BUDGET_MS else (255, 130, 130)
    metric_y = rect.top + 42
    metric_lines = [
        f"N {sim.enemy_count}   Frame {sim.total_ms_ema:4.2f} ms",
        f"Path {sim.path_ms_ema:4.2f} ms   Expanded {sim.expanded_this_frame}",
        f"Detour {sim.detour_ema:4.2f}   Stuck {sim.stuck_count}   Reached {sim.reached}",
    ]
    if sim.method == "Flow Field":
        metric_lines[1] = f"Flow build {sim.path_ms_ema:4.2f} ms   {sim.recomputes_per_min():.1f}/min"

    for idx, line in enumerate(metric_lines):
        line_color = budget_color if idx == 0 else (215, 220, 230)
        _draw_text(game, line, rect.left + 14, metric_y + idx * 18, line_color)

    area = pygame.Rect(rect.left + 12, rect.top + 102, rect.width - 24, rect.height - 116)
    scale, left, top, map_rect = _draw_obstacles(game.screen, area, sim)
    old_clip = game.screen.get_clip()
    game.screen.set_clip(map_rect)

    player_pos = _scripted_player(sim.frame)
    if len(sim.player_trace) >= 2:
        points = [_world_to_rect(pos, area, sim)[0] for pos in sim.player_trace]
        pygame.draw.lines(game.screen, (90, 180, 255), False, points, 2)

    _draw_flow_arrows(game.screen, sim, area)
    _draw_paths(game.screen, sim, area)
    _draw_steering_rays(game.screen, sim, player_pos, area)

    player_screen = _world_to_rect(player_pos, area, sim)[0]
    player_size = max(24, int(96 * scale))
    if len(sim.player_trace) >= 2:
        player_direction = sim.player_trace[-1] - sim.player_trace[-2]
    else:
        player_direction = pygame.Vector2(1, 0)
    _draw_player_sprite(game.screen, player_screen, player_size, player_direction)

    enemy_size = max(12, int(42 * scale))
    enemy_img = _load_eval_image("./Img/enemy_1.png", (enemy_size, enemy_size))
    for enemy in sim.enemies:
        pos = _world_to_rect(enemy["pos"], area, sim)[0]
        if enemy_img:
            image = enemy_img.copy()
            if enemy["stuck_counted"]:
                image.fill((255, 120, 120, 255), special_flags=pygame.BLEND_RGBA_MULT)
            game.screen.blit(image, image.get_rect(center=pos))
        else:
            enemy_color = (255, 100, 100) if enemy["stuck_counted"] else color
            pygame.draw.circle(game.screen, enemy_color, pos, max(2, int(6 * scale)))

    game.screen.set_clip(old_clip)


def _draw_eval1(game):
    game.screen.fill((15, 17, 23))
    sim = game.eval1_sim
    title = game.font.render("Evaluation 1 - Pathfinding Stress Test", True, (255, 230, 140))
    game.screen.blit(title, (28, 18))

    enemy_count = N_VALUES[game.eval1_enemy_idx]
    state = "Paused" if game.eval1_paused else "Running"
    hint = (
        f"{state} | Method {sim.method} ({game.eval1_method_idx + 1}/{len(METHODS)}) | "
        f"N={enemy_count} ({game.eval1_enemy_idx + 1}/{len(N_VALUES)}) | "
        "Left/Right method, Up/Down N, P pause, R reset, ESC back."
    )
    _draw_text(game, hint, 30, 54, (180, 190, 205))
    design = (
        "N sweep: 10, 30, 60, 120, 200, 300. "
        "Uses production chunk obstacles and the same local flow-field window as gameplay."
    )
    _draw_text(game, design, 30, 74, (145, 154, 170))

    reset_btn = pygame.Rect(game.screen_width - 290, 18, 120, 42)
    back_btn = pygame.Rect(game.screen_width - 150, 18, 120, 42)
    GF.draw_button(game.screen, reset_btn, "Reset", font=game.HUD_font)
    GF.draw_button(game.screen, back_btn, "Back", font=game.HUD_font)

    margin = 24
    top = 106
    rect = pygame.Rect(
        margin,
        top,
        game.screen_width - margin * 2,
        game.screen_height - top - margin,
    )
    _draw_panel(game, sim, rect)

    return reset_btn, back_btn


def test_screen_eval1(game, events):
    _ensure_eval1_state(game)

    reset_btn = pygame.Rect(game.screen_width - 290, 18, 120, 42)
    back_btn = pygame.Rect(game.screen_width - 150, 18, 120, 42)

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.test_screen = 4
                return
            if event.key == pygame.K_r:
                _reset_eval1(game)
            elif event.key == pygame.K_p:
                game.eval1_paused = not game.eval1_paused
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                _switch_eval1_method(game, 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                _switch_eval1_method(game, -1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                _switch_eval1_enemy_count(game, 1)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                _switch_eval1_enemy_count(game, -1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn.collidepoint(event.pos):
                game.test_screen = 4
                return
            if reset_btn.collidepoint(event.pos):
                _reset_eval1(game)

    if not game.eval1_paused:
        game.eval1_sim.update()
        game.eval1_sim.print_summary_if_ready()

    _draw_eval1(game)
