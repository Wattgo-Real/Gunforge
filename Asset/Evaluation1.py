import heapq
import math
import random
import time
from collections import deque

import pygame

import Asset.Function as GF
from Asset.ImageLoader import load_image_surface


METHODS = ("Steering", "A*", "Dijkstra", "Flow Field")
N_VALUES = (10, 30, 60, 120)
DT = 1.0 / 60.0
CELL_SIZE = 32
GRID_W = 42
GRID_H = 30
WORLD_W = GRID_W * CELL_SIZE
WORLD_H = GRID_H * CELL_SIZE
ENEMY_SPEED = 92.0
PATH_REFRESH_FRAMES = 18
FRAME_BUDGET_MS = 16.0

METHOD_COLORS = {
    "Steering": (245, 175, 90),
    "A*": (115, 190, 255),
    "Dijkstra": (155, 230, 145),
    "Flow Field": (235, 135, 245),
}
EVAL1_IMAGE_CACHE = {}
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


def _fixed_obstacles():
    rects = [
        (6, 5, 6, 5),
        (17, 3, 7, 4),
        (29, 6, 7, 5),
        (8, 15, 8, 4),
        (23, 13, 6, 7),
        (32, 18, 6, 5),
        (13, 24, 8, 4),
        (4, 22, 5, 5),
        (30, 25, 7, 3),
    ]
    blocked = set()
    for x, y, w, h in rects:
        for cx in range(x, x + w):
            for cy in range(y, y + h):
                blocked.add((cx, cy))
    return blocked, rects


BLOCKED_CELLS, OBSTACLE_RECTS = _fixed_obstacles()
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


def _cell_to_world(cell):
    return pygame.Vector2((cell[0] + 0.5) * CELL_SIZE, (cell[1] + 0.5) * CELL_SIZE)


def _world_to_cell(pos):
    return (
        max(0, min(GRID_W - 1, int(pos.x // CELL_SIZE))),
        max(0, min(GRID_H - 1, int(pos.y // CELL_SIZE))),
    )


def _is_walkable(cell):
    x, y = cell
    return 0 <= x < GRID_W and 0 <= y < GRID_H and cell not in BLOCKED_CELLS


def _nearest_walkable(cell):
    if _is_walkable(cell):
        return cell
    queue = [cell]
    seen = {cell}
    while queue:
        curr = queue.pop(0)
        for dx, dy in NEIGHBORS_4:
            nxt = (curr[0] + dx, curr[1] + dy)
            if nxt in seen:
                continue
            if _is_walkable(nxt):
                return nxt
            if 0 <= nxt[0] < GRID_W and 0 <= nxt[1] < GRID_H:
                seen.add(nxt)
                queue.append(nxt)
    return (0, 0)


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


def _search_path(start, goal, use_heuristic):
    start = _nearest_walkable(start)
    goal = _nearest_walkable(goal)
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
            if not _is_walkable(nxt):
                continue
            new_cost = cost_so_far[curr] + _edge_cost(curr, nxt)
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + (_heuristic(nxt, goal) if use_heuristic else 0.0)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = curr

    return _reconstruct(came_from, start, goal), cost_so_far.get(goal), expanded


def _build_flow_field(goal):
    goal = _nearest_walkable(goal)
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
            if not _is_walkable(nxt):
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
            direction = _cell_to_world(best) - _cell_to_world(cell)
            if direction.length_squared() > 0:
                flow[cell] = direction.normalize()
    return dist, flow, expanded


def _scripted_player(frame):
    t = frame / 60.0
    cx = WORLD_W * 0.5
    cy = WORLD_H * 0.5
    return pygame.Vector2(
        cx + math.sin(t * 0.9) * 360 + math.sin(t * 1.7) * 120,
        cy + math.cos(t * 0.7) * 250,
    )


def _spawn_enemy_from_rng(rng):
    for _ in range(80):
        edge = rng.randrange(4)
        if edge == 0:
            cell = (rng.randrange(GRID_W), 1)
        elif edge == 1:
            cell = (rng.randrange(GRID_W), GRID_H - 2)
        elif edge == 2:
            cell = (1, rng.randrange(GRID_H))
        else:
            cell = (GRID_W - 2, rng.randrange(GRID_H))
        cell = _nearest_walkable(cell)
        pos = _cell_to_world(cell)
        return {
            "pos": pos,
            "start": pos.copy(),
            "path": [],
            "path_idx": 0,
            "stuck_time": 0.0,
            "stuck_counted": False,
            "path_len": 0.0,
        }
    return {
        "pos": pygame.Vector2(16, 16),
        "start": pygame.Vector2(16, 16),
        "path": [],
        "path_idx": 0,
        "stuck_time": 0.0,
        "stuck_counted": False,
        "path_len": 0.0,
    }


def _spawn_enemies(count):
    rng = random.Random(42 + count * 17)
    return [_spawn_enemy_from_rng(rng) for _ in range(count)]


def _near_obstacle(cell):
    for dx, dy in NEIGHBORS_8:
        if (cell[0] + dx, cell[1] + dy) in BLOCKED_CELLS:
            return True
    return False


def _line_crosses_obstacle(start_pos, end_pos):
    distance = max(1.0, start_pos.distance_to(end_pos))
    steps = max(2, int(distance / (CELL_SIZE * 0.5)))
    for i in range(1, steps + 1):
        pos = start_pos.lerp(end_pos, i / steps)
        if _world_to_cell(pos) in BLOCKED_CELLS:
            return True
    return False


def _try_move(pos, velocity):
    next_pos = pos + velocity
    if _is_walkable(_world_to_cell(next_pos)):
        return next_pos

    slide_x = pygame.Vector2(pos.x + velocity.x, pos.y)
    if _is_walkable(_world_to_cell(slide_x)):
        return slide_x

    slide_y = pygame.Vector2(pos.x, pos.y + velocity.y)
    if _is_walkable(_world_to_cell(slide_y)):
        return slide_y

    return pos


class LivePathEvaluation:
    def __init__(self, method, enemy_count):
        self.method = method
        self.enemy_count = enemy_count
        self.rng = random.Random(9000 + enemy_count * 13 + METHODS.index(method))
        self.player_trace = deque(maxlen=180)
        self.reset(enemy_count)

    def reset(self, enemy_count=None):
        if enemy_count is not None:
            self.enemy_count = enemy_count
        self.frame = 0
        self.enemies = _spawn_enemies(self.enemy_count)
        self.flow_dist = {}
        self.flow = {}
        self.flow_goal = None
        self.path_cache = {}
        self.recomputes = 0
        self.expanded_this_frame = 0
        self.reached = 0
        self.path_ms_ema = 0.0
        self.total_ms_ema = 0.0
        self.detour_ema = 1.0
        self.stuck_count = 0
        self.player_trace.clear()

    def update(self):
        t_total = time.perf_counter()
        self.frame += 1
        self.expanded_this_frame = 0
        path_ms = 0.0
        detour_values = []

        player_pos = _scripted_player(self.frame)
        player_cell = _nearest_walkable(_world_to_cell(player_pos))
        self.player_trace.append(player_pos.copy())

        if self.method == "Flow Field" and self.flow_goal != player_cell:
            t0 = time.perf_counter()
            self.flow_dist, self.flow, expanded = _build_flow_field(player_cell)
            path_ms += (time.perf_counter() - t0) * 1000.0
            self.expanded_this_frame += expanded
            self.flow_goal = player_cell
            self.recomputes += 1

        for idx, enemy in enumerate(self.enemies):
            pos = enemy["pos"]
            start_cell = _nearest_walkable(_world_to_cell(pos))
            direction = pygame.Vector2(0, 0)

            if self.method == "Steering":
                target = player_pos
                direction = target - pos
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                detour_values.append(1.65 if _line_crosses_obstacle(pos, player_pos) else 1.0)

            elif self.method in ("A*", "Dijkstra"):
                needs_path = self.frame % PATH_REFRESH_FRAMES == idx % PATH_REFRESH_FRAMES
                needs_path = needs_path or not enemy["path"] or enemy["path_idx"] >= len(enemy["path"])
                if needs_path:
                    cache_key = (self.method, start_cell, player_cell)
                    if cache_key in self.path_cache:
                        path, cost = self.path_cache[cache_key]
                        expanded = 0
                    else:
                        t0 = time.perf_counter()
                        path, cost, expanded = _search_path(start_cell, player_cell, self.method == "A*")
                        path_ms += (time.perf_counter() - t0) * 1000.0
                        self.path_cache[cache_key] = (path, cost)
                        if len(self.path_cache) > 500:
                            self.path_cache.clear()
                    self.expanded_this_frame += expanded
                    enemy["path"] = path
                    enemy["path_idx"] = 1 if len(path) > 1 else 0
                    if cost is not None:
                        euclid = max(1.0, pos.distance_to(player_pos))
                        detour_values.append((cost * CELL_SIZE) / euclid)

                if enemy["path"] and enemy["path_idx"] < len(enemy["path"]):
                    target = _cell_to_world(enemy["path"][enemy["path_idx"]])
                    if pos.distance_to(target) < CELL_SIZE * 0.35:
                        enemy["path_idx"] += 1
                else:
                    target = player_pos

                direction = target - pos
                if direction.length_squared() > 0:
                    direction = direction.normalize()

            else:
                direction = self.flow.get(start_cell, pygame.Vector2(0, 0))
                if start_cell in self.flow_dist:
                    euclid = max(1.0, pos.distance_to(player_pos))
                    detour_values.append((self.flow_dist[start_cell] * CELL_SIZE) / euclid)

            old_pos = pos.copy()
            new_pos = _try_move(pos, direction * ENEMY_SPEED * DT)
            moved = old_pos.distance_to(new_pos)
            enemy["pos"] = new_pos
            enemy["path_len"] += moved

            if _near_obstacle(_world_to_cell(new_pos)) and moved < ENEMY_SPEED * DT * 0.35:
                enemy["stuck_time"] += DT
                if enemy["stuck_time"] > 2.0 and not enemy["stuck_counted"]:
                    enemy["stuck_counted"] = True
            else:
                enemy["stuck_time"] = 0.0

            if new_pos.distance_to(player_pos) < 22:
                self.reached += 1
                self.enemies[idx] = _spawn_enemy_from_rng(self.rng)

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


def _ensure_eval1_state(game):
    if getattr(game, "_eval1_initialized", False):
        return
    game.eval1_enemy_idx = 1
    game.eval1_paused = False
    enemy_count = N_VALUES[game.eval1_enemy_idx]
    game.eval1_sims = [LivePathEvaluation(method, enemy_count) for method in METHODS]
    game._eval1_initialized = True


def _reset_eval1(game):
    _ensure_eval1_state(game)
    enemy_count = N_VALUES[game.eval1_enemy_idx]
    for sim in game.eval1_sims:
        sim.reset(enemy_count)


def _draw_text(game, text, x, y, color=(230, 230, 230), font=None):
    surf = (font or game.HUD_font).render(text, True, color)
    game.screen.blit(surf, (x, y))
    return surf.get_height()


def _world_to_rect(pos, area):
    scale = min(area.width / WORLD_W, area.height / WORLD_H)
    draw_w = WORLD_W * scale
    draw_h = WORLD_H * scale
    left = area.left + (area.width - draw_w) * 0.5
    top = area.top + (area.height - draw_h) * 0.5
    return pygame.Vector2(left + pos.x * scale, top + pos.y * scale), scale, left, top


def _draw_obstacles(screen, area):
    _, scale, left, top = _world_to_rect(pygame.Vector2(0, 0), area)
    map_rect = pygame.Rect(left, top, WORLD_W * scale, WORLD_H * scale)
    background = _load_eval_image("./Img/background.png", map_rect.size)
    if background:
        screen.blit(background, map_rect)
    else:
        pygame.draw.rect(screen, (14, 17, 24), map_rect)
    pygame.draw.rect(screen, (58, 64, 78), map_rect, 1)

    for idx, (ox, oy, ow, oh) in enumerate(OBSTACLE_RECTS):
        rect = pygame.Rect(
            left + ox * CELL_SIZE * scale,
            top + oy * CELL_SIZE * scale,
            ow * CELL_SIZE * scale,
            oh * CELL_SIZE * scale,
        )
        obstacle_path = OBSTACLE_IMAGE_PATHS[idx % len(OBSTACLE_IMAGE_PATHS)]
        obstacle = _load_eval_image(obstacle_path, (rect.width * 1.45, rect.height * 1.65))
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
        start, scale, _, _ = _world_to_rect(_cell_to_world(cell), area)
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
        points = [_world_to_rect(_cell_to_world(cell), area)[0] for cell in enemy["path"]]
        if len(points) >= 2:
            pygame.draw.lines(screen, color, False, points, 1)
            drawn += 1
        if drawn >= 10:
            break


def _draw_steering_rays(screen, sim, player_pos, area):
    if sim.method != "Steering":
        return
    for enemy in sim.enemies[:10]:
        start = _world_to_rect(enemy["pos"], area)[0]
        end = _world_to_rect(player_pos, area)[0]
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
    scale, left, top, map_rect = _draw_obstacles(game.screen, area)
    old_clip = game.screen.get_clip()
    game.screen.set_clip(map_rect)

    player_pos = _scripted_player(sim.frame)
    if len(sim.player_trace) >= 2:
        points = [_world_to_rect(pos, area)[0] for pos in sim.player_trace]
        pygame.draw.lines(game.screen, (90, 180, 255), False, points, 2)

    _draw_flow_arrows(game.screen, sim, area)
    _draw_paths(game.screen, sim, area)
    _draw_steering_rays(game.screen, sim, player_pos, area)

    player_screen = _world_to_rect(player_pos, area)[0]
    player_size = max(12, int(30 * scale))
    player_img = _load_eval_image("./Img/Ball.png", (player_size, player_size))
    if player_img:
        game.screen.blit(player_img, player_img.get_rect(center=player_screen))
    else:
        pygame.draw.circle(game.screen, (80, 185, 255), player_screen, max(4, int(9 * scale)))
        pygame.draw.circle(game.screen, (235, 250, 255), player_screen, max(4, int(9 * scale)), 1)

    enemy_size = max(12, int(42 * scale))
    enemy_img = _load_eval_image("./Img/enemy_1.png", (enemy_size, enemy_size))
    for enemy in sim.enemies:
        pos = _world_to_rect(enemy["pos"], area)[0]
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
    title = game.font.render("Evaluation 1 - Pathfinding Methods Live Comparison", True, (255, 230, 140))
    game.screen.blit(title, (28, 18))

    enemy_count = N_VALUES[game.eval1_enemy_idx]
    state = "Paused" if game.eval1_paused else "Running"
    hint = (
        f"{state} | Same obstacle map, same scripted player, N={enemy_count}. "
        "E changes N, P pauses, R resets, ESC returns."
    )
    _draw_text(game, hint, 30, 54, (180, 190, 205))

    reset_btn = pygame.Rect(game.screen_width - 290, 18, 120, 42)
    back_btn = pygame.Rect(game.screen_width - 150, 18, 120, 42)
    GF.draw_button(game.screen, reset_btn, "Reset", font=game.HUD_font)
    GF.draw_button(game.screen, back_btn, "Back", font=game.HUD_font)

    margin = 22
    top = 88
    gap = 14
    panel_w = (game.screen_width - margin * 2 - gap) // 2
    panel_h = (game.screen_height - top - margin - gap) // 2
    for idx, sim in enumerate(game.eval1_sims):
        col = idx % 2
        row = idx // 2
        rect = pygame.Rect(
            margin + col * (panel_w + gap),
            top + row * (panel_h + gap),
            panel_w,
            panel_h,
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
            elif event.key == pygame.K_e:
                game.eval1_enemy_idx = (game.eval1_enemy_idx + 1) % len(N_VALUES)
                _reset_eval1(game)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn.collidepoint(event.pos):
                game.test_screen = 4
                return
            if reset_btn.collidepoint(event.pos):
                _reset_eval1(game)

    if not game.eval1_paused:
        for sim in game.eval1_sims:
            sim.update()

    _draw_eval1(game)
