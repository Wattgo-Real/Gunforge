import heapq
import math
import random
import sys
import time

import pygame

import Asset.Function as GF


METHODS = ("Steering", "A*", "Dijkstra", "Flow Field")
N_VALUES = (10, 30, 60, 120, 200)
FRAME_BUDGET_MS = 16.0
SIM_FRAMES = 126
DT = 1.0 / 60.0
CELL_SIZE = 32
GRID_W = 42
GRID_H = 30
ENEMY_SPEED = 92.0
PATH_REFRESH_FRAMES = 18
CHUNK_WORLD_SIZE = 1000


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
NEIGHBORS_8 = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))


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

    while frontier:
        _, curr = heapq.heappop(frontier)
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

    return _reconstruct(came_from, start, goal), cost_so_far.get(goal)


def _build_flow_field(goal):
    goal = _nearest_walkable(goal)
    frontier = [(0.0, goal)]
    dist = {goal: 0.0}

    while frontier:
        curr_cost, curr = heapq.heappop(frontier)
        if curr_cost > dist[curr]:
            continue
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
    return dist, flow


def _scripted_player(frame):
    t = frame / 60.0
    cx = GRID_W * CELL_SIZE * 0.5
    cy = GRID_H * CELL_SIZE * 0.5
    return pygame.Vector2(
        cx + math.sin(t * 0.9) * 360 + math.sin(t * 1.7) * 120,
        cy + math.cos(t * 0.7) * 250,
    )


def _spawn_enemies(count):
    rng = random.Random(42 + count * 17)
    enemies = []
    attempts = 0
    while len(enemies) < count and attempts < count * 40:
        attempts += 1
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
        enemies.append({
            "pos": _cell_to_world(cell),
            "start": _cell_to_world(cell),
            "path": [],
            "path_idx": 0,
            "stuck_time": 0.0,
            "stuck_counted": False,
            "path_len": 0.0,
            "detour_sum": 0.0,
            "detour_samples": 0,
        })
    return enemies


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


def _path_distance(cells):
    if len(cells) < 2:
        return 0.0
    total = 0.0
    for a, b in zip(cells, cells[1:]):
        total += _edge_cost(a, b) * CELL_SIZE
    return total


def _estimate_memory_kb(method, n, flow_dist=None, flow=None, avg_path_len=0):
    total = sys.getsizeof(BLOCKED_CELLS) + len(BLOCKED_CELLS) * 16
    total += GRID_W * GRID_H
    if method in ("A*", "Dijkstra"):
        total += n * max(1, avg_path_len) * 8
    elif method == "Flow Field":
        total += sys.getsizeof(flow_dist or {}) + len(flow_dist or {}) * 24
        total += sys.getsizeof(flow or {}) + len(flow or {}) * 24
    chunk_count = max(1, math.ceil((GRID_W * CELL_SIZE) / CHUNK_WORLD_SIZE) * math.ceil((GRID_H * CELL_SIZE) / CHUNK_WORLD_SIZE))
    return total / 1024.0 / chunk_count


def _simulate(method, enemy_count):
    enemies = _spawn_enemies(enemy_count)
    flow_dist = {}
    flow = {}
    flow_goal = None
    recomputes = 0
    path_ms = 0.0
    other_ms = 0.0
    path_cache = {}

    for frame in range(SIM_FRAMES):
        player_pos = _scripted_player(frame)
        player_cell = _nearest_walkable(_world_to_cell(player_pos))

        if method == "Flow Field" and flow_goal != player_cell:
            t0 = time.perf_counter()
            flow_dist, flow = _build_flow_field(player_cell)
            path_ms += (time.perf_counter() - t0) * 1000.0
            flow_goal = player_cell
            recomputes += 1

        t_other = time.perf_counter()
        for idx, enemy in enumerate(enemies):
            pos = enemy["pos"]
            start_cell = _nearest_walkable(_world_to_cell(pos))
            target = player_pos

            if method == "Steering":
                direction = target - pos
                if direction.length_squared() > 0:
                    direction = direction.normalize()
                enemy["detour_sum"] += 1.65 if _line_crosses_obstacle(pos, target) else 1.0
                enemy["detour_samples"] += 1
            elif method in ("A*", "Dijkstra"):
                needs_path = frame % PATH_REFRESH_FRAMES == idx % PATH_REFRESH_FRAMES
                needs_path = needs_path or not enemy["path"] or enemy["path_idx"] >= len(enemy["path"])
                if needs_path:
                    cache_key = (method, start_cell, player_cell)
                    if cache_key in path_cache:
                        path, cost = path_cache[cache_key]
                    else:
                        t0 = time.perf_counter()
                        path, cost = _search_path(start_cell, player_cell, method == "A*")
                        path_ms += (time.perf_counter() - t0) * 1000.0
                        path_cache[cache_key] = (path, cost)
                    enemy["path"] = path
                    enemy["path_idx"] = 1 if len(path) > 1 else 0
                    euclid = max(1.0, pos.distance_to(player_pos))
                    if cost is not None:
                        enemy["detour_sum"] += (cost * CELL_SIZE) / euclid
                        enemy["detour_samples"] += 1
                if enemy["path"] and enemy["path_idx"] < len(enemy["path"]):
                    target = _cell_to_world(enemy["path"][enemy["path_idx"]])
                    if pos.distance_to(target) < CELL_SIZE * 0.35:
                        enemy["path_idx"] += 1
                direction = target - pos
                if direction.length_squared() > 0:
                    direction = direction.normalize()
            else:
                direction = flow.get(start_cell, pygame.Vector2(0, 0))
                euclid = max(1.0, pos.distance_to(player_pos))
                if start_cell in flow_dist:
                    enemy["detour_sum"] += (flow_dist[start_cell] * CELL_SIZE) / euclid
                    enemy["detour_samples"] += 1

            old_pos = pos
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
        other_ms += (time.perf_counter() - t_other) * 1000.0

    total_path_len = sum(enemy["path_len"] for enemy in enemies)
    final_player = _scripted_player(SIM_FRAMES - 1)
    straight = sum(max(1.0, enemy["start"].distance_to(final_player)) for enemy in enemies)
    fallback_ratio = total_path_len / straight if straight > 0 else 1.0
    sampled = [
        enemy["detour_sum"] / enemy["detour_samples"]
        for enemy in enemies
        if enemy["detour_samples"] > 0
    ]
    detour_ratio = sum(sampled) / len(sampled) if sampled else fallback_ratio
    stuck_count = sum(1 for enemy in enemies if enemy["stuck_counted"])
    avg_path_len = sum(len(enemy["path"]) for enemy in enemies) / max(1, len(enemies))

    path_frame = path_ms / SIM_FRAMES
    other_frame = other_ms / SIM_FRAMES
    total_frame = path_frame + other_frame
    sim_minutes = (SIM_FRAMES * DT) / 60.0
    recompute_rate = recomputes / sim_minutes if method == "Flow Field" and sim_minutes > 0 else 0.0
    memory_kb = _estimate_memory_kb(method, enemy_count, flow_dist, flow, avg_path_len)

    return {
        "method": method,
        "n": enemy_count,
        "fps": 1000.0 / max(0.001, total_frame),
        "path_ms": path_frame,
        "other_ms": other_frame,
        "total_ms": total_frame,
        "detour": detour_ratio,
        "stuck": stuck_count,
        "memory_kb": memory_kb,
        "flow_recompute": recompute_rate,
    }


def _run_benchmark():
    results = {}
    for method in METHODS:
        results[method] = {}
        for n in N_VALUES:
            results[method][n] = _simulate(method, n)
    return results


def _recommend(results):
    recommendations = []
    for n in N_VALUES:
        budget_rows = {method: results[method][n] for method in METHODS if results[method][n]["total_ms"] <= FRAME_BUDGET_MS}
        if not budget_rows:
            best = min((results[method][n] for method in METHODS), key=lambda row: row["total_ms"])
            recommendations.append((n, best["method"]))
            continue

        steering = budget_rows.get("Steering")
        astar = budget_rows.get("A*")
        dijkstra = budget_rows.get("Dijkstra")
        flow = budget_rows.get("Flow Field")

        steering_ok = steering and steering["detour"] <= 1.55 and steering["stuck"] <= max(1, int(n * 0.04))
        astar_ok = astar and astar["detour"] <= 1.35 and astar["stuck"] <= max(1, int(n * 0.03))
        dijkstra_ok = dijkstra and dijkstra["detour"] <= 1.35 and dijkstra["stuck"] <= max(1, int(n * 0.03))

        if n <= 30 and steering_ok:
            method = "Steering"
        elif n <= 60 and astar_ok:
            method = "A*"
        elif n <= 60 and dijkstra_ok and (not astar or astar["total_ms"] > FRAME_BUDGET_MS):
            method = "Dijkstra"
        elif flow:
            method = "Flow Field"
        else:
            method = min(budget_rows.values(), key=lambda row: (row["stuck"], row["detour"], row["total_ms"]))["method"]
        recommendations.append((n, method))

    ranges = []
    start_n, current = recommendations[0]
    prev_n = start_n
    for n, method in recommendations[1:]:
        if method != current:
            ranges.append((start_n, prev_n, current))
            start_n, current = n, method
        prev_n = n
    ranges.append((start_n, prev_n, current))
    return recommendations, ranges


def _ensure_eval1_state(game):
    if getattr(game, "_eval1_initialized", False):
        return
    game.eval1_method_idx = 0
    game.eval1_running = True
    t0 = time.perf_counter()
    game.eval1_results = _run_benchmark()
    game.eval1_elapsed_ms = (time.perf_counter() - t0) * 1000.0
    game.eval1_recommendations, game.eval1_ranges = _recommend(game.eval1_results)
    game.eval1_running = False
    game._eval1_initialized = True


def _format_ranges(ranges):
    parts = []
    for start, end, method in ranges:
        label = f"N={start}" if start == end else f"N={start}-{end}"
        parts.append(f"{label}: {method}")
    return " | ".join(parts)


def _analysis_notes(results, recommendations):
    used = {method for _, method in recommendations}
    notes = []
    if "Steering" not in used:
        worst_detour = max(results["Steering"][n]["detour"] for n in N_VALUES)
        notes.append(f"Steering excluded: detour peaks at {worst_detour:.2f} in obstacle map.")
    if "Dijkstra" not in used:
        d200 = results["Dijkstra"][200]["total_ms"]
        notes.append(f"Dijkstra dominated: {d200:.1f} ms at N=200 and no better detour than A*/Flow.")
    return notes


def _draw_text(game, text, x, y, color=(230, 230, 230), font=None):
    surf = (font or game.HUD_font).render(text, True, color)
    game.screen.blit(surf, (x, y))
    return surf.get_height()


def _draw_results(game):
    game.screen.fill((18, 22, 28))
    title = game.font.render("Evaluation 1: Pathfinder Crossover Benchmark", True, (255, 230, 140))
    game.screen.blit(title, (40, 28))

    subtitle = "Fixed seed/scripted player, pure chasers, N={10,30,60,120,200}, 16 ms frame budget"
    _draw_text(game, subtitle, 40, 62, (190, 200, 210))
    _draw_text(game, f"Benchmark time: {game.eval1_elapsed_ms:.1f} ms   [M] method details   [R] rerun   [ESC] back", 40, 84, (170, 190, 220))

    ranges = _format_ranges(game.eval1_ranges)
    _draw_text(game, "Recommended crossover: " + ranges, 40, 118, (120, 255, 160), game.mid_font)
    notes = _analysis_notes(game.eval1_results, game.eval1_recommendations)
    for idx, note in enumerate(notes):
        _draw_text(game, note, 40, 142 + idx * 20, (255, 190, 120))

    y = 190
    headers = ["N", "Best", "Total", "FPS", "Path", "Other", "Detour", "Stuck", "Mem/Chunk"]
    xs = [40, 105, 230, 315, 390, 470, 555, 650, 735]
    for x, h in zip(xs, headers):
        _draw_text(game, h, x, y, (255, 255, 255))
    y += 24

    for n, method in game.eval1_recommendations:
        row = game.eval1_results[method][n]
        color = (130, 255, 150) if row["total_ms"] <= FRAME_BUDGET_MS else (255, 120, 120)
        values = [
            str(n),
            method,
            f"{row['total_ms']:.2f}",
            f"{row['fps']:.1f}",
            f"{row['path_ms']:.2f}",
            f"{row['other_ms']:.2f}",
            f"{row['detour']:.2f}",
            str(row["stuck"]),
            f"{row['memory_kb']:.1f} KB",
        ]
        for x, value in zip(xs, values):
            _draw_text(game, value, x, y, color)
        y += 22

    method = METHODS[game.eval1_method_idx]
    y += 30
    _draw_text(game, f"Details: {method}", 40, y, (255, 220, 120), game.mid_font)
    y += 30
    detail_headers = ["N", "FPS", "Path ms", "Other ms", "Total ms", "Detour", "Stuck", "Mem KB", "FF recompute/min"]
    detail_xs = [40, 95, 165, 260, 360, 465, 550, 625, 720]
    for x, h in zip(detail_xs, detail_headers):
        _draw_text(game, h, x, y, (255, 255, 255))
    y += 24

    for n in N_VALUES:
        row = game.eval1_results[method][n]
        color = (210, 230, 250) if row["total_ms"] <= FRAME_BUDGET_MS else (255, 150, 150)
        values = [
            str(n),
            f"{row['fps']:.1f}",
            f"{row['path_ms']:.2f}",
            f"{row['other_ms']:.2f}",
            f"{row['total_ms']:.2f}",
            f"{row['detour']:.2f}",
            str(row["stuck"]),
            f"{row['memory_kb']:.1f}",
            f"{row['flow_recompute']:.1f}" if method == "Flow Field" else "-",
        ]
        for x, value in zip(detail_xs, values):
            _draw_text(game, value, x, y, color)
        y += 22

    _draw_map_preview(game, 1040, 150, 500, 360)

    back_btn = pygame.Rect(40, game.screen_height - 88, 220, 56)
    GF.draw_button(game.screen, back_btn, "Back", font=game.font)
    return back_btn


def _draw_map_preview(game, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(game.screen, (28, 32, 40), rect)
    pygame.draw.rect(game.screen, (120, 130, 150), rect, 1)
    sx = w / (GRID_W * CELL_SIZE)
    sy = h / (GRID_H * CELL_SIZE)

    for ox, oy, ow, oh in OBSTACLE_RECTS:
        obstacle_rect = pygame.Rect(
            x + int(ox * CELL_SIZE * sx),
            y + int(oy * CELL_SIZE * sy),
            max(1, int(ow * CELL_SIZE * sx)),
            max(1, int(oh * CELL_SIZE * sy)),
        )
        pygame.draw.rect(game.screen, (90, 70, 95), obstacle_rect)

    points = []
    for frame in range(0, SIM_FRAMES, 4):
        pos = _scripted_player(frame)
        points.append((x + int(pos.x * sx), y + int(pos.y * sy)))
    if len(points) >= 2:
        pygame.draw.lines(game.screen, (120, 220, 255), False, points, 2)
    _draw_text(game, "Scripted player path / obstacle grid", x, y - 24, (190, 200, 220))


def test_screen_eval1(game, events):
    _ensure_eval1_state(game)

    back_btn = None
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.test_screen = 4
            elif event.key == pygame.K_m:
                game.eval1_method_idx = (game.eval1_method_idx + 1) % len(METHODS)
            elif event.key == pygame.K_r:
                game._eval1_initialized = False
                _ensure_eval1_state(game)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_btn and back_btn.collidepoint(event.pos):
                game.test_screen = 4

    back_btn = _draw_results(game)
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_btn.collidepoint(event.pos):
            game.test_screen = 4
