from typing import TYPE_CHECKING

import numpy
import pygame

if TYPE_CHECKING:
    from Start import Game

import random

from Asset.Card import Card
from Asset.Enemies import EnemyManager
from Asset.GameSetting import (
    COLOR_CONFIG,
    ENTITY_TYPE,
    GAME_CONFIG,
    GRID_CONFIG,
    PROBABILITY_CONFIG,
    UI_CONFIG,
)
from Asset.Pickups import Altar, Obstacle, WorldChunkManager, XPOrb
from Asset.Player import Player
from Asset.ShopConfig import STAT_UPGRADES, card_key_to_tuple, ensure_shop_state
from Asset.SpatialGrid import NoneGrid, Quadtree, SpatialGrid
from Asset.Weapons import BulletManager, Gun


def _ensure_runtime_state(game: "Game"):
    """Initialize gameplay state once when entering screen 1."""
    if getattr(game, "_screen1_initialised", False):
        return

    if game.partition_method == "Quadtree":
        game.spatial_grid_dict = Quadtree()
    elif game.partition_method == "NoneGrid":
        game.spatial_grid_dict = NoneGrid()
    elif game.partition_method == "SpatialGrid":
        game.spatial_grid_dict = SpatialGrid()

    game.enemy_manager = EnemyManager(spatial_grid_dict=game.spatial_grid_dict)
    game.bullet_manager = BulletManager(spatial_grid_dict=game.spatial_grid_dict)
    game.world = WorldChunkManager(spatial_grid_dict=game.spatial_grid_dict, seed=42)
    game.xp_orbs = []
    game.gun_pickups = []
    game.run_start_time = game.now_time
    game.run_summary = None
    game.message_queue = []  # list of [text, timer_left, color]
    game.effects_queue = []  # list of [effect : {}, timer_left]
    game.player = Player(
        position=pygame.Vector2(0, 0),
        radius=15,
        color=(0, 150, 255),
        bullet_manager=game.bullet_manager,
    )
    _apply_shop_upgrades(game)
    game.leveling_up = False
    game.level_up_options = []
    game.level_up_scroll_offsets = [0, 0, 0]
    game.altar_choosing = False
    game.altar_options = []
    game.active_altar = None
    game.map_overview_enabled = False
    game._screen1_initialised = True


def reset_screen1(game: "Game"):
    """Reset gameplay state for a new run. Called by menu / game-over screen."""
    if game.partition_method == "Quadtree":
        game.spatial_grid_dict = Quadtree()
    elif game.partition_method == "NoneGrid":
        game.spatial_grid_dict = NoneGrid()
    elif game.partition_method == "SpatialGrid":
        game.spatial_grid_dict = SpatialGrid()

    if hasattr(game, "bullet_manager"):
        game.bullet_manager.reset(spatial_grid_dict=game.spatial_grid_dict)
    else:
        game.bullet_manager = BulletManager(spatial_grid_dict=game.spatial_grid_dict)

    if hasattr(game, "enemy_manager"):
        game.enemy_manager.spatial_grid_dict = game.spatial_grid_dict
        game.enemy_manager.reset()
    else:
        game.enemy_manager = EnemyManager(spatial_grid_dict=game.spatial_grid_dict)

    if hasattr(game, "world"):
        game.world.spatial_grid_dict = game.spatial_grid_dict
        game.world.reset(seed=42)
    else:
        game.world = WorldChunkManager(
            spatial_grid_dict=game.spatial_grid_dict, seed=42
        )

    if hasattr(game, "player"):
        game.player.reset_run(pygame.Vector2(0, 0))
    else:
        game.player = Player(
            position=pygame.Vector2(0, 0),
            radius=15,
            color=(0, 150, 255),
            bullet_manager=game.bullet_manager,
        )
    _apply_shop_upgrades(game)

    game.xp_orbs = []
    game.gun_pickups = []
    game.run_start_time = game.now_time
    game.run_summary = None
    game.message_queue = []
    game.effects_queue = []
    game.leveling_up = False
    game.level_up_options = []
    game.level_up_scroll_offsets = [0, 0, 0]
    game.altar_choosing = False
    game.altar_options = []
    game.active_altar = None
    game.map_overview_enabled = False
    game._screen1_initialised = True


def _add_card_to_inventory(player, card):
    for i, slot in enumerate(player.inventory):
        if slot is None:
            player.inventory[i] = card
            return True
    return False


def _apply_shop_upgrades(game: "Game"):
    ensure_shop_state(game)
    player = game.player

    hp_level = game.shop_upgrades.get("hp", 0)
    damage_level = game.shop_upgrades.get("damage", 0)
    speed_level = game.shop_upgrades.get("speed", 0)

    player.max_hp += hp_level * STAT_UPGRADES["hp"]["amount"]
    player.hp = player.max_hp
    player.damage_multiplier += damage_level * STAT_UPGRADES["damage"]["amount"]
    speed_bonus = speed_level * STAT_UPGRADES["speed"]["amount"]
    player.bonus_speed += speed_bonus
    player.max_velocity += speed_bonus

    for key in sorted(game.shop_owned_cards):
        card_type, card_id = card_key_to_tuple(key)
        _add_card_to_inventory(player, Card(type=card_type, inter_type=card_id))


class GunPickup:
    def __init__(self, position, gun_info):
        self.pos2D = pygame.Vector2(position)
        self.gun_info = gun_info
        self.radius = 34
        self.alive = True
        self.pulse_timer = 0.0
        self.message_timer = 0.0

    def update(self, delta_time, game: "Game"):
        self.pulse_timer += delta_time
        self.message_timer = max(0.0, self.message_timer - delta_time)

        if self.pos2D.distance_to(game.player.pos2D) > GAME_CONFIG["gun_pickup_radius"]:
            return False

        for i, slot in enumerate(game.player.weapon_list):
            if slot is None:
                game.player.weapon_list[i] = Gun(self.gun_info, game.bullet_manager)
                self.alive = False
                game.message_queue.append(
                    [f"New gun acquired! Slot {i + 1}", 4.0, (255, 220, 120)]
                )
                return True

        if self.message_timer <= 0:
            self.message_timer = 1.5
            game.message_queue.append(["Weapon slots full", 1.5, (255, 140, 120)])
        return False

    def draw(self, screen, game: "Game"):
        screen_pos = game.to_screen(self.pos2D)
        pulse = 1.0 + 0.12 * abs(pygame.math.Vector2(1, 0).rotate(self.pulse_timer * 220).y)
        glow_radius = int(self.radius * 1.35 * pulse)
        pygame.draw.circle(screen, (255, 210, 90), screen_pos, glow_radius, 2)
        pygame.draw.circle(screen, (60, 45, 25), screen_pos, self.radius)
        pygame.draw.circle(screen, (255, 235, 150), screen_pos, self.radius, 2)

        barrel_start = (int(screen_pos.x - 12), int(screen_pos.y + 2))
        barrel_end = (int(screen_pos.x + 18), int(screen_pos.y - 8))
        pygame.draw.line(screen, (210, 210, 220), barrel_start, barrel_end, 7)
        pygame.draw.line(screen, (70, 55, 45), barrel_start, barrel_end, 2)
        grip_rect = pygame.Rect(0, 0, 12, 20)
        grip_rect.center = (int(screen_pos.x - 6), int(screen_pos.y + 12))
        pygame.draw.rect(screen, (140, 85, 45), grip_rect, border_radius=3)


def _create_boss_reward_gun_info(game: "Game"):
    num_cards = random.randint(2, 5)
    random_cards = _get_random_cards(game, count=num_cards)
    return {
        "cooldown": 0.25,
        "reload": 1.5,
        "scatter_angle": 8,
        "capacity": 30,
        "max_slots": random.randint(6, 15),
        "card_list": random_cards + [
            Card(type=0, inter_type=2),
        ],
    }


def _drop_boss_reward(game: "Game", position):
    if not hasattr(game, "gun_pickups"):
        game.gun_pickups = []

    game.gun_pickups.append(GunPickup(position, _create_boss_reward_gun_info(game)))
    game.message_queue.append(["BOSS DOWN - gun dropped!", 5.0, (255, 220, 120)])


def _get_random_cards(game: "Game", count=3):
    """Pick cards based on inverse weights in PROBABILITY_CONFIG without duplicates."""
    tiers = list(PROBABILITY_CONFIG.keys())
    # weights: higher weight = lower probability (score = 1/weight)
    scores = [1.0 / PROBABILITY_CONFIG[tier]["weight"] for tier in tiers]

    selected_cards = []
    selected_keys = set()

    total_available_items = sum(len(PROBABILITY_CONFIG[tier]["items"]) for tier in tiers)
    max_draws = min(count, total_available_items)

    attempts = 0
    while len(selected_cards) < max_draws and attempts < 1000:
        attempts += 1
        chosen_tier_name = random.choices(tiers, weights=scores, k=1)[0]
        tier_data = PROBABILITY_CONFIG[chosen_tier_name]
        if not tier_data["items"]:
            continue
        item_config = random.choice(tier_data["items"])
        key = (item_config["type"], item_config["id"])
        if key not in selected_keys:
            selected_keys.add(key)
            card = Card(type=item_config["type"], inter_type=item_config["id"])
            selected_cards.append(card)
    return selected_cards


def _draw_level_up_screen(game: "Game", events):
    """Draw the card selection screen when leveling up."""
    # Dark overlay
    overlay = pygame.Surface((game.screen_width, game.screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    game.screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("Arial", 54, bold=True)
    title_text = title_font.render("LEVEL UP! CHOOSE A CARD", True, (255, 255, 255))
    game.screen.blit(
        title_text, (game.screen_width // 2 - title_text.get_width() // 2, 80)
    )

    card_w, card_h = 260, 400
    spacing = 50
    total_w = 3 * card_w + 2 * spacing
    start_x = (game.screen_width - total_w) // 2
    start_y = (game.screen_height - card_h) // 2 + 40

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    hovered_card_idx = -1
    for i in range(len(game.level_up_options)):
        card_x = start_x + i * (card_w + spacing)
        card_y = start_y
        if pygame.Rect(card_x, card_y, card_w, card_h).collidepoint(mouse_pos):
            hovered_card_idx = i
            break

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_clicked = True
            elif event.button == 4 and hovered_card_idx != -1:  # Scroll Up
                game.level_up_scroll_offsets[hovered_card_idx] = max(
                    0, game.level_up_scroll_offsets[hovered_card_idx] - 20
                )
            elif event.button == 5 and hovered_card_idx != -1:  # Scroll Down
                game.level_up_scroll_offsets[hovered_card_idx] += 20

    for i, card in enumerate(game.level_up_options):
        x = start_x + i * (card_w + spacing)
        y = start_y
        rect = pygame.Rect(x, y, card_w, card_h)

        is_hovered = rect.collidepoint(mouse_pos)
        border_color = (255, 255, 100) if is_hovered else (200, 200, 200)
        bg_color = (60, 60, 60, 255) if is_hovered else (40, 40, 40, 255)

        # Card Background
        pygame.draw.rect(game.screen, bg_color, rect)
        pygame.draw.rect(game.screen, border_color, rect, 3)

        name, info = card.get_info()

        # 1. Name
        name_surf = game.mid_font.render(name, True, (255, 255, 255))
        game.screen.blit(name_surf, (x + (card_w - name_surf.get_width()) // 2, y + 20))

        # 2. Icon area
        icon_rect = pygame.Rect(x + 40, y + 50, 180, 140)
        pygame.draw.rect(game.screen, (30, 30, 30), icon_rect)
        card.draw(game.screen, icon_rect)
        pygame.draw.rect(game.screen, (100, 100, 100), icon_rect, 1)

        # 3. Description
        def draw_wrapped_text(surface, text, font, color, draw_rect, card_idx):
            words = text.split(" ")
            lines = []
            curr = []
            for ws in words:
                for idx, w in enumerate(ws.split("\n")):
                    if not w:
                        continue
                    test = " ".join(curr + [w])
                    if font.size(test)[0] <= draw_rect.width and idx == 0:
                        curr.append(w)
                    else:
                        lines.append(" ".join(curr))
                        curr = [w]
            lines.append(" ".join(curr))

            total_h = len(lines) * font.get_linesize()
            max_scroll = max(0, total_h - draw_rect.height)
            if game.level_up_scroll_offsets[card_idx] > max_scroll:
                game.level_up_scroll_offsets[card_idx] = max_scroll

            old_clip = surface.get_clip()
            surface.set_clip(draw_rect)

            line_y = draw_rect.top - game.level_up_scroll_offsets[card_idx]
            for line in lines:
                if not line:
                    continue
                if (
                    line_y + font.get_linesize() > draw_rect.top
                    and line_y < draw_rect.bottom
                ):
                    s = font.render(line, True, color)
                    surface.blit(s, (draw_rect.left, line_y))
                line_y += font.get_linesize()

            surface.set_clip(old_clip)

        desc_rect = pygame.Rect(x + 20, y + 200, card_w - 40, 160)
        draw_wrapped_text(
            game.screen, info, game.HUD_font, (230, 230, 230), desc_rect, i
        )

        if is_hovered and mouse_clicked:
            # Selection logic
            for idx in range(len(game.player.inventory)):
                if game.player.inventory[idx] is None:
                    game.player.inventory[idx] = card
                    break
            else:
                game.player.inventory.append(card)

            game.leveling_up = False
            game.level_up_options = []
            game.message_queue.append([f"Acquired: {name}", 2.5, (100, 255, 120)])
            return


def _altar_buff_info(buff_type: str):
    amounts = GAME_CONFIG["altar_buff_amount"]
    if buff_type == "hp":
        return ("Health +", f"+{amounts['hp']} Max HP", (220, 70, 70))
    if buff_type == "damage":
        return ("Damage +", f"+{int(amounts['damage'] * 100)}% Damage", (255, 190, 70))
    if buff_type == "speed":
        return ("Move Speed +", f"+{amounts['speed']} Speed", (100, 220, 140))
    return (buff_type, buff_type, (220, 220, 220))


def _draw_altar_buff_icon(surface, rect, buff_type: str, color):
    cx, cy = rect.center
    if buff_type == "hp":
        points = [
            (cx, cy + rect.height * 0.28),
            (cx - rect.width * 0.34, cy - rect.height * 0.05),
            (cx - rect.width * 0.20, cy - rect.height * 0.32),
            (cx, cy - rect.height * 0.18),
            (cx + rect.width * 0.20, cy - rect.height * 0.32),
            (cx + rect.width * 0.34, cy - rect.height * 0.05),
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)
    elif buff_type == "damage":
        start = (cx - rect.width * 0.28, cy + rect.height * 0.24)
        end = (cx + rect.width * 0.24, cy - rect.height * 0.28)
        pygame.draw.line(surface, color, start, end, 10)
        pygame.draw.polygon(
            surface,
            color,
            [
                (end[0] + rect.width * 0.12, end[1] - rect.height * 0.12),
                (end[0] + rect.width * 0.02, end[1] + rect.height * 0.18),
                (end[0] - rect.width * 0.16, end[1] - rect.height * 0.02),
            ],
        )
        pygame.draw.line(surface, (255, 255, 255), start, end, 2)
    elif buff_type == "speed":
        pygame.draw.polygon(
            surface,
            color,
            [
                (cx - rect.width * 0.18, cy - rect.height * 0.28),
                (cx + rect.width * 0.26, cy),
                (cx - rect.width * 0.18, cy + rect.height * 0.28),
            ],
        )
        for offset in (-24, 0, 24):
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (cx - rect.width * 0.38, cy + offset),
                (cx - rect.width * 0.08, cy + offset),
                4,
            )


def _draw_altar_choice_screen(game: "Game", events):
    overlay = pygame.Surface((game.screen_width, game.screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    game.screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("Arial", 54, bold=True)
    title_text = title_font.render("ALTAR BLESSING", True, (255, 245, 210))
    game.screen.blit(
        title_text, (game.screen_width // 2 - title_text.get_width() // 2, 80)
    )

    card_w, card_h = 260, 340
    spacing = 50
    total_w = 3 * card_w + 2 * spacing
    start_x = (game.screen_width - total_w) // 2
    start_y = (game.screen_height - card_h) // 2 + 40

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = any(
        event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events
    )

    for i, buff_type in enumerate(game.altar_options):
        x = start_x + i * (card_w + spacing)
        y = start_y
        rect = pygame.Rect(x, y, card_w, card_h)
        title, detail, color = _altar_buff_info(buff_type)
        is_hovered = rect.collidepoint(mouse_pos)
        border_color = (255, 245, 120) if is_hovered else (210, 190, 130)
        bg_color = (58, 48, 32, 255) if is_hovered else (36, 34, 30, 255)

        pygame.draw.rect(game.screen, bg_color, rect)
        pygame.draw.rect(game.screen, border_color, rect, 3)

        name_surf = game.mid_font.render(title, True, (255, 255, 255))
        game.screen.blit(name_surf, (x + (card_w - name_surf.get_width()) // 2, y + 24))

        icon_rect = pygame.Rect(x + 50, y + 80, 160, 130)
        pygame.draw.rect(game.screen, (24, 24, 24), icon_rect)
        _draw_altar_buff_icon(game.screen, icon_rect, buff_type, color)
        pygame.draw.rect(game.screen, (120, 110, 90), icon_rect, 1)

        detail_surf = game.font.render(detail, True, color)
        game.screen.blit(
            detail_surf, (x + (card_w - detail_surf.get_width()) // 2, y + 240)
        )

        if is_hovered and mouse_clicked:
            game.player.apply_altar_buff(buff_type)
            if game.active_altar is not None:
                game.active_altar.used = True
                game.world.remove_altar(game.active_altar)
            game.altar_choosing = False
            game.altar_options = []
            game.active_altar = None
            game.message_queue.append([f"Altar: {detail}", 2.5, (255, 230, 120)])
            return


def _handle_collisions(game: "Game"):
    player = game.player

    # Enemy bullet vs player
    for bullet in list(game.enemy_manager.all_enemy_bullets()):
        if bullet.pos2D.distance_to(player.pos2D) < player.radius + bullet.radius:
            if player.take_damage(bullet.damage):
                bullet.alive = False

    # Enemy contact damage
    for e in game.enemy_manager.enemies:
        if e.pos2D.distance_to(player.pos2D) < e.radius + player.radius:
            if e.attack_timer <= 0 and e.ai in ("chase", "runner") and not e.is_boss:
                if player.take_damage(e.damage):
                    e.attack_timer = e.attack_cooldown
            elif e.is_boss:
                player.take_damage(e.damage * 1.2)

    # Enemy vs Enemy collision
    for e1 in game.enemy_manager.enemies:
        # Spatial Partition Grid
        for e2 in game.spatial_grid_dict.get_entities_near_by_type(
            e1.pos2D, ENTITY_TYPE["enemy"], range_cells=1
        ):
            if e1.uuid == e2.uuid:
                continue

            dist = e1.pos2D.distance_to(e2.pos2D)
            min_dist = e1.radius + e2.radius
            if dist < min_dist:
                # Push them apart
                overlap = min_dist - dist
                if dist > 0:
                    push_dir = (e1.pos2D - e2.pos2D).normalize()
                else:
                    # Exact overlap, push in a random direction
                    import random

                    angle = random.uniform(0, 360)
                    push_dir = pygame.Vector2(1, 0).rotate(angle)

                # Shift both enemies
                e1.pos2D += push_dir * (overlap * 0.5)
                e2.pos2D -= push_dir * (overlap * 0.5)


def _handle_player_bullets(game: "Game"):
    player = game.player

    # Bullet vs enemy & obstacle
    for bullet in game.bullet_manager.bullets:
        if bullet.isKill:
            continue

        # Bullet vs obstacle
        hit_obstacle = False
        for obs in Obstacle.get_nearby_obstacles(bullet.pos2D, game.spatial_grid_dict):
            if obs.collides_circle(bullet.pos2D, bullet.radius):
                bullet.triger_hit(obs, effect_queue=game.effects_queue)
                hit_obstacle = True
                break

        if hit_obstacle:
            continue
        # Bullet vs enemy
        # Spatial Partition Grid is used to find the nearest enemy in the area around the bullet.
        for entity in game.spatial_grid_dict.get_entities_near_by_type(
            bullet.pos2D, ENTITY_TYPE["enemy"], range_cells=1
        ):
            if entity.uuid in bullet.hit_enemies:
                continue

            if (
                entity.pos2D.distance_to(bullet.pos2D)
                < bullet.radius + entity.radius + 5
            ):
                bullet.triger_hit(entity, effect_queue=game.effects_queue)
                if not entity.alive:
                    if getattr(entity, "reward_claimed", False):
                        continue
                    entity.reward_claimed = True
                    game.xp_orbs.append(
                        XPOrb(entity.pos2D.copy(), value=entity.xp_drop)
                    )
                    player.add_kill()
                    if entity.is_boss:
                        _drop_boss_reward(game, entity.pos2D.copy())
                break


def _draw_effect(game: "Game"):
    for effect in game.effects_queue:
        effect[1] -= game.delta_time
        effect_info = effect[0]

        time_left = effect[1]
        if time_left <= 0:
            game.effects_queue.remove(effect)
            continue

        if "disappearing_circle" in effect_info:
            for info in effect_info["disappearing_circle"]:
                color = info["color"]
                alpha = int(color[3] * (time_left / info["total_time"]))
                position = info["pos_2D"]
                position = game.to_screen(position)
                radius = info["radius"]
                effect_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    effect_surf,
                    (color[0], color[1], color[2], alpha),
                    (radius, radius),
                    radius,
                )
                game.screen.blit(
                    effect_surf, (position.x - radius, position.y - radius)
                )


def _draw_hud(game: "Game"):
    player = game.player
    elapsed = game.now_time - game.run_start_time
    minutes, seconds = divmod(int(elapsed), 60)

    # HP bar (top-left)
    hp_bar_w = 260
    hp_bar_h = 22
    hp_x, hp_y = 20, 20
    pygame.draw.rect(game.screen, (30, 30, 30), (hp_x, hp_y, hp_bar_w, hp_bar_h))
    hp_ratio = max(0.0, player.hp / player.max_hp) if player.max_hp > 0 else 0
    pygame.draw.rect(
        game.screen, (220, 60, 60), (hp_x, hp_y, int(hp_bar_w * hp_ratio), hp_bar_h)
    )
    pygame.draw.rect(game.screen, (220, 220, 220), (hp_x, hp_y, hp_bar_w, hp_bar_h), 2)
    hp_text = game.HUD_font.render(
        f"HP {int(player.hp)}/{int(player.max_hp)}", True, (255, 255, 255)
    )
    game.screen.blit(hp_text, (hp_x + 8, hp_y + 3))

    # XP bar (below HP)
    xp_y = hp_y + hp_bar_h + 6
    xp_bar_h = 14
    pygame.draw.rect(game.screen, (30, 30, 30), (hp_x, xp_y, hp_bar_w, xp_bar_h))
    xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0
    pygame.draw.rect(
        game.screen, (140, 200, 255), (hp_x, xp_y, int(hp_bar_w * xp_ratio), xp_bar_h)
    )
    pygame.draw.rect(game.screen, (220, 220, 220), (hp_x, xp_y, hp_bar_w, xp_bar_h), 1)
    lvl_text = game.HUD_font.render(
        f"Lv {player.level}  XP {player.xp}/{player.xp_to_next}", True, (240, 240, 240)
    )
    game.screen.blit(lvl_text, (hp_x + 8, xp_y - 2))

    # Dash Cooldown (below XP)
    dash_bar_y = xp_y + xp_bar_h + 6
    dash_bar_h = 6
    pygame.draw.rect(
        game.screen, (30, 30, 30), (hp_x, dash_bar_y, hp_bar_w, dash_bar_h)
    )
    if player.dash_cooldown_timer > 0:
        dash_ratio = 1.0 - (player.dash_cooldown_timer / player.dash_cooldown)
        pygame.draw.rect(
            game.screen,
            (100, 100, 100),
            (hp_x, dash_bar_y, int(hp_bar_w * dash_ratio), dash_bar_h),
        )
    else:
        pygame.draw.rect(
            game.screen, (100, 255, 100), (hp_x, dash_bar_y, hp_bar_w, dash_bar_h)
        )
    pygame.draw.rect(
        game.screen, (220, 220, 220), (hp_x, dash_bar_y, hp_bar_w, dash_bar_h), 1
    )

    # Stats line (right of bars)
    stats_text = game.HUD_font.render(
        f"Time {minutes:02d}:{seconds:02d}   Kills {player.kills}   Pts {player.points}",
        True,
        (240, 240, 240),
    )
    game.screen.blit(stats_text, (hp_x + hp_bar_w + 20, hp_y + 3))

    # Boss countdown until spawn
    if not game.enemy_manager.boss_spawned:
        remain = max(0, game.enemy_manager.boss_spawn_time - game.enemy_manager.elapsed)
        bm, bs = divmod(int(remain), 60)
        boss_text = game.HUD_font.render(
            f"BOSS in {bm:02d}:{bs:02d}", True, (255, 180, 120)
        )
        game.screen.blit(boss_text, (hp_x + hp_bar_w + 20, xp_y - 2))


def _draw_boss_bar(game: "Game"):
    boss = game.enemy_manager.boss
    if boss is None or not boss.alive:
        return
    bar_w = min(900, game.screen_width - 200)
    bar_h = 24
    bar_x = (game.screen_width - bar_w) // 2
    bar_y = game.screen_height - bar_h - 30
    pygame.draw.rect(game.screen, (40, 0, 0), (bar_x, bar_y, bar_w, bar_h))
    ratio = max(0.0, boss.hp / boss.max_hp)
    pygame.draw.rect(
        game.screen, (200, 30, 30), (bar_x, bar_y, int(bar_w * ratio), bar_h)
    )
    pygame.draw.rect(game.screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2)
    label = game.font.render("BOSS", True, (255, 255, 255))
    game.screen.blit(label, (bar_x + (bar_w - label.get_width()) // 2, bar_y - 4))


def _draw_messages(game: "Game"):
    y = 120
    for entry in list(game.message_queue):
        text, timer, color = entry
        entry[1] -= game.delta_time
        if entry[1] <= 0:
            game.message_queue.remove(entry)
            continue
        alpha = min(255, int(255 * (timer / 1.5))) if timer < 1.5 else 255
        msg_surf = game.font.render(text, True, color)
        msg_surf.set_alpha(alpha)
        x = (game.screen_width - msg_surf.get_width()) // 2
        game.screen.blit(msg_surf, (x, y))
        y += 32


def _draw_map_overview(game: "Game"):
    world = game.world
    if not getattr(world, "generated", None):
        return

    panel_size = min(480, game.screen_width - 40, game.screen_height - 120)
    if panel_size < 220:
        return

    panel = pygame.Rect(
        game.screen_width - panel_size - 20,
        92,
        panel_size,
        panel_size,
    )
    pad = 18
    map_rect = panel.inflate(-pad * 2, -pad * 2 - 42)
    map_rect.top = panel.top + 46

    chunk_size = world.CHUNK_SIZE
    chunks = list(world.generated)
    player_chunk = (
        int(game.player.pos2D.x // chunk_size),
        int(game.player.pos2D.y // chunk_size),
    )
    chunks.append(player_chunk)

    min_cx = min(cx for cx, _ in chunks) - 1
    max_cx = max(cx for cx, _ in chunks) + 1
    min_cy = min(cy for _, cy in chunks) - 1
    max_cy = max(cy for _, cy in chunks) + 1
    min_x = min_cx * chunk_size
    max_x = (max_cx + 1) * chunk_size
    min_y = min_cy * chunk_size
    max_y = (max_cy + 1) * chunk_size
    world_w = max(1.0, max_x - min_x)
    world_h = max(1.0, max_y - min_y)
    scale = min(map_rect.width / world_w, map_rect.height / world_h)
    draw_w = world_w * scale
    draw_h = world_h * scale
    origin_x = map_rect.centerx - draw_w / 2
    origin_y = map_rect.centery - draw_h / 2

    def to_map(pos):
        return pygame.Vector2(
            origin_x + (pos.x - min_x) * scale,
            origin_y + (max_y - pos.y) * scale,
        )

    overlay = pygame.Surface(panel.size, pygame.SRCALPHA)
    overlay.fill((10, 12, 18, 222))
    pygame.draw.rect(overlay, (120, 125, 145, 230), overlay.get_rect(), 2)
    game.screen.blit(overlay, panel.topleft)

    title = game.font.render("Generated Map", True, (235, 238, 245))
    game.screen.blit(title, (panel.left + pad, panel.top + 12))
    obstacle_count = sum(len(records) for records in world.obstacle_records.values())
    altar_count = sum(
        1
        for records in world.altar_records.values()
        for record in records
        if not record["used"]
    )
    meta = game.HUD_font.render(
        f"Chunks {len(world.generated)}   Active {len(world.active_chunks)}   Obstacles {obstacle_count}   Altars {altar_count}",
        True,
        (185, 190, 205),
    )
    game.screen.blit(meta, (panel.left + pad, panel.top + 34))

    pygame.draw.rect(game.screen, (16, 18, 26), map_rect)
    pygame.draw.rect(game.screen, (62, 68, 82), map_rect, 1)

    for cx, cy in world.generated:
        left_bottom = pygame.Vector2(cx * chunk_size, cy * chunk_size)
        right_top = pygame.Vector2((cx + 1) * chunk_size, (cy + 1) * chunk_size)
        a = to_map(left_bottom)
        b = to_map(right_top)
        rect = pygame.Rect(
            min(a.x, b.x),
            min(a.y, b.y),
            max(1, abs(b.x - a.x)),
            max(1, abs(b.y - a.y)),
        )
        fill = (33, 38, 48) if (cx, cy) != player_chunk else (42, 70, 92)
        pygame.draw.rect(game.screen, fill, rect)
        pygame.draw.rect(game.screen, (64, 70, 84), rect, 1)

    cam = game.camera_position
    view_a = to_map(pygame.Vector2(cam.x - game.screen_width / 2, cam.y - game.screen_height / 2))
    view_b = to_map(pygame.Vector2(cam.x + game.screen_width / 2, cam.y + game.screen_height / 2))
    view_rect = pygame.Rect(
        min(view_a.x, view_b.x),
        min(view_a.y, view_b.y),
        max(2, abs(view_b.x - view_a.x)),
        max(2, abs(view_b.y - view_a.y)),
    )
    pygame.draw.rect(game.screen, (245, 245, 245), view_rect, 1)

    for records in world.obstacle_records.values():
        for record in records:
            pos = pygame.Vector2(record["pos"])
            size = pygame.Vector2(record["size"])
            half = size / 2
            a = to_map(pos + pygame.Vector2(-half.x, -half.y))
            b = to_map(pos + pygame.Vector2(half.x, half.y))
            rect = pygame.Rect(
                min(a.x, b.x),
                min(a.y, b.y),
                max(3, abs(b.x - a.x)),
                max(3, abs(b.y - a.y)),
            )
            pygame.draw.rect(game.screen, (120, 105, 145), rect)

    for records in world.altar_records.values():
        for record in records:
            if record["used"]:
                continue
            pos = to_map(pygame.Vector2(record["pos"]))
            pygame.draw.circle(game.screen, (245, 210, 95), pos, 4)

    for enemy in game.enemy_manager.enemies:
        pos = to_map(enemy.pos2D)
        color = (255, 80, 80) if not enemy.is_boss else (255, 45, 45)
        radius = 3 if not enemy.is_boss else 6
        pygame.draw.circle(game.screen, color, pos, radius)

    player_pos = to_map(game.player.pos2D)
    pygame.draw.circle(game.screen, (70, 180, 255), player_pos, 6)
    pygame.draw.circle(game.screen, (235, 250, 255), player_pos, 6, 1)

    legend_y = panel.bottom - 22
    legend_items = [
        ((70, 180, 255), "Player"),
        ((255, 80, 80), "Enemy"),
        ((120, 105, 145), "Obstacle"),
        ((245, 210, 95), "Altar"),
    ]
    x = panel.left + pad
    for color, label in legend_items:
        pygame.draw.circle(game.screen, color, (x + 5, legend_y + 6), 4)
        text = game.HUD_font.render(label, True, (205, 210, 220))
        game.screen.blit(text, (x + 14, legend_y))
        x += text.get_width() + 58


def _draw_player_invuln_flash(game: "Game"):
    if game.player.invincible_timer > 0:
        screen_pos = game.to_screen(game.player.pos2D)
        flash_alpha = int(
            120 * (game.player.invincible_timer / GAME_CONFIG["player_invincible_time"])
        )
        flash_surf = pygame.Surface(
            (game.player.radius * 4, game.player.radius * 4), pygame.SRCALPHA
        )
        pygame.draw.circle(
            flash_surf,
            (255, 80, 80, flash_alpha),
            (game.player.radius * 2, game.player.radius * 2),
            game.player.radius * 2,
        )
        game.screen.blit(
            flash_surf,
            (
                screen_pos.x - game.player.radius * 2,
                screen_pos.y - game.player.radius * 2,
            ),
        )


def _draw_gun_info_overlay(game: "Game", events, selected_slot: bool):
    box_w = UI_CONFIG["gun_box_w"]
    box_h = UI_CONFIG["gun_box_h"]
    slot_size = UI_CONFIG["slot_size"]
    info_x = UI_CONFIG["info_x"]
    pad_x = UI_CONFIG["gun_box_padding_x"]
    pad_y = UI_CONFIG["gun_box_padding_y"]
    spacing_y = UI_CONFIG["gun_box_spacing_y"]

    positions = [
        (pad_x, pad_y),
        (pad_x, pad_y + spacing_y),
        (game.screen_width - (box_w + pad_x), pad_y),
        (game.screen_width - (box_w + pad_x), pad_y + spacing_y),
    ]

    # Mouse state for click selection
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = any(
        event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events
    )

    # --- Draw Gun Boxes ---
    for i in range(4):
        x, y = positions[i]
        gun = game.player.weapon_list[i]

        # Create box surface
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((30, 30, 30, 180))  # Semi-transparent dark gray
        pygame.draw.rect(
            box_surf, (200, 200, 200, 255), box_surf.get_rect(), 2
        )  # Border

        # 1. ID Number (top-left)
        id_text = game.font.render(str(i + 1), True, (255, 255, 255))
        box_surf.blit(id_text, (10, 5))

        if gun is None:
            # Display "empty" in center
            empty_text = game.font.render("empty", True, (120, 120, 120))
            text_rect = empty_text.get_rect(center=(box_w // 2, box_h // 2))
            box_surf.blit(empty_text, text_rect)
        else:
            # 2. Gun Appearance (left side square)
            gun_icon_rect = pygame.Rect(40, 70, 100, 100)
            pygame.draw.rect(
                box_surf, (80, 120, 200), gun_icon_rect
            )  # Placeholder color
            pygame.draw.rect(box_surf, (255, 255, 255), gun_icon_rect, 2)

            # 3. Gun Information (top-right)
            info_x = 200
            info_y = 15
            stats = {
                "Cooldown": round(gun.cooldown, 2),
                "Reload": round(gun.reload, 2),
                "Scatter": round(gun.scatter_angle, 2),
                "Capacity": f"{gun.capacity_left}/{gun.capacity}",
            }
            for j, (key, value) in enumerate(stats.items()):
                if key == "Cooldown":
                    color = COLOR_CONFIG["cooldown"]
                elif key == "Reload":
                    color = COLOR_CONFIG["reload"]
                elif key == "Scatter":
                    color = COLOR_CONFIG["scatter_angle"]
                elif key == "Capacity":
                    color = COLOR_CONFIG["capacity"]

                stat_text = game.HUD_font.render(f"{key}: {value}", True, color)
                box_surf.blit(stat_text, (info_x, info_y + j * 22))

            # 3.5. Cooldown & Reload Bars
            bar_x = 400
            bar_w, bar_h = 180, 12

            # Cooldown Bar
            cd_ratio = (
                1 - (gun.cooldown_timer / gun.cooldown) if gun.cooldown > 0 else 1
            )
            pygame.draw.rect(
                box_surf, (40, 40, 40), (bar_x, info_y, bar_w, bar_h)
            )  # BG
            pygame.draw.rect(
                box_surf,
                COLOR_CONFIG["cooldown"],
                (bar_x, info_y, int(bar_w * cd_ratio), bar_h),
            )  # Fill
            pygame.draw.rect(
                box_surf, (200, 200, 200), (bar_x, info_y, bar_w, bar_h), 1
            )  # Border

            # Reload Bar
            rl_ratio = 1 - (gun.reload_timer / gun.reload) if gun.reload > 0 else 1
            pygame.draw.rect(
                box_surf, (40, 40, 40), (bar_x, info_y + 22, bar_w, bar_h)
            )  # BG
            pygame.draw.rect(
                box_surf,
                COLOR_CONFIG["reload"],
                (bar_x, info_y + 22, int(bar_w * rl_ratio), bar_h),
            )  # Fill
            pygame.draw.rect(
                box_surf, (200, 200, 200), (bar_x, info_y + 22, bar_w, bar_h), 1
            )  # Border

            pygame.draw.line(box_surf, (255, 255, 255), (0, 30), (info_x - 20, 30), 2)
            pygame.draw.line(
                box_surf, (255, 255, 255), (info_x - 20, 0), (info_x - 20, box_h), 4
            )

            # Hover Detection & Slot Drawing
            m_x, m_y = pygame.mouse.get_pos()

            # 4. Card Max Slots (bottom-right)
            slots_total_w = 10 * slot_size
            slots_start_x = info_x
            slots_y = box_h - 2 * slot_size - 15

            for s in range(gun.card_max_slots):
                slot_rect = pygame.Rect(
                    slots_start_x + (s % 10) * slot_size,
                    slots_y + (s // 10) * slot_size,
                    slot_size,
                    slot_size,
                )
                pygame.draw.rect(box_surf, (150, 150, 150), slot_rect, 1)

                # Draw selection highlight
                if (
                    game.selected_slot_info
                    and game.selected_slot_info["type"] == "gun"
                    and game.selected_slot_info["gun_idx"] == i
                    and game.selected_slot_info["slot_idx"] == s
                ):
                    pygame.draw.rect(box_surf, (255, 255, 100), slot_rect, 3)

                # Draw card icon if exists
                card = gun.card_list[s]
                if card:
                    card.draw(box_surf, slot_rect)

        # Blit box to screen
        game.screen.blit(box_surf, (x, y))

        # Draw highlight if this gun slot is selected for moving
        selected_gun_slot = getattr(game, "selected_gun_slot", None)
        if selected_gun_slot is not None and selected_gun_slot == i:
            pygame.draw.rect(
                game.screen, (255, 255, 100), (x, y, box_w, box_h), 4
            )

    # --- Draw Inventory Grid ---
    grid_cell_size = UI_CONFIG["grid_cell_size"]
    grid_cols = UI_CONFIG["grid_cols"]
    grid_rows = UI_CONFIG["grid_rows"]
    grid_w = grid_cols * grid_cell_size
    grid_h = grid_rows * grid_cell_size

    grid_start_x = (game.screen_width - grid_w) // 2
    grid_start_y = game.screen_height - grid_h - UI_CONFIG["inv_bottom_padding"]

    grid_surface = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    # grid_surface.fill((20, 20, 20, 100)) # Optional background
    for r in range(grid_rows):
        for c in range(grid_cols):
            idx = r * grid_cols + c
            rect = pygame.Rect(
                c * grid_cell_size, r * grid_cell_size, grid_cell_size, grid_cell_size
            )
            pygame.draw.rect(grid_surface, (200, 200, 200, 200), rect, 1)

            # Draw selection highlight
            if (
                game.selected_slot_info
                and game.selected_slot_info["type"] == "inv"
                and game.selected_slot_info["slot_idx"] == idx
            ):
                pygame.draw.rect(grid_surface, (255, 255, 100), rect, 3)

            # Draw card icon
            if idx < len(game.player.inventory):
                card = game.player.inventory[idx]
                if card:
                    card.draw(grid_surface, rect)

    game.screen.blit(grid_surface, (grid_start_x, grid_start_y))

    # --- Draw Tooltip and clicked slot ---
    m_x, m_y = pygame.mouse.get_pos()

    # --- Draw Discard Zone (above backpack bottom right) ---
    discard_w = 220
    discard_h = 50
    discard_x = grid_start_x + grid_w - discard_w
    discard_y = grid_start_y - discard_h - 15
    discard_rect = pygame.Rect(discard_x, discard_y, discard_w, discard_h)

    # Check hover and determine if discard is valid
    is_hovered_discard = discard_rect.collidepoint(m_x, m_y)
    can_discard = False
    if game.selected_slot_info is not None:
        can_discard = True
    elif getattr(game, "selected_gun_slot", None) is not None:
        gun_count = sum(1 for g in game.player.weapon_list if g is not None)
        if gun_count > 1:
            can_discard = True

    # Draw premium styled discard zone
    if can_discard:
        bg_color = (180, 50, 50, 220) if is_hovered_discard else (120, 30, 30, 180)
        border_color = (255, 120, 120) if is_hovered_discard else (180, 60, 60)
        text_color = (255, 255, 255)
    else:
        bg_color = (60, 60, 60, 100) if is_hovered_discard else (40, 40, 40, 80)
        border_color = (100, 100, 100)
        text_color = (120, 120, 120)

    discard_surf = pygame.Surface((discard_w, discard_h), pygame.SRCALPHA)
    discard_surf.fill(bg_color)
    pygame.draw.rect(discard_surf, border_color, discard_surf.get_rect(), 2)

    label_str = "DISCARD"
    if game.selected_slot_info is not None:
        label_str = "DISCARD CARD"
    elif getattr(game, "selected_gun_slot", None) is not None:
        label_str = "DISCARD GUN"

    discard_text = game.font.render(label_str, True, text_color)
    text_rect = discard_text.get_rect(center=(discard_w // 2, discard_h // 2))
    discard_surf.blit(discard_text, text_rect)

    game.screen.blit(discard_surf, (discard_x, discard_y))

    # --- Click and Hover Detection ---
    clicked_card_slot = None
    clicked_gun_idx = None
    clicked_trash = False
    hovered_card = None

    # Check gun card slots for hover/click
    for i in range(4):
        gun = game.player.weapon_list[i]
        if not gun:
            continue
        gx, gy = positions[i]
        slots_start_x = gx + info_x
        slots_start_y = gy + box_h - 2 * slot_size - 15
        for s in range(gun.card_max_slots):
            slot_rect = pygame.Rect(
                slots_start_x + (s % 10) * slot_size,
                slots_start_y + (s // 10) * slot_size,
                slot_size,
                slot_size,
            )
            if slot_rect.collidepoint(m_x, m_y):
                clicked_card_slot = {"type": "gun", "gun_idx": i, "slot_idx": s}
                if gun.card_list[s]:
                    hovered_card = gun.card_list[s]
                break
        if clicked_card_slot:
            break

    # Check inventory grid for hover/click
    if not clicked_card_slot:
        for idx in range(40):
            r, c = idx // grid_cols, idx % grid_cols
            slot_rect = pygame.Rect(
                grid_start_x + c * grid_cell_size,
                grid_start_y + r * grid_cell_size,
                grid_cell_size,
                grid_cell_size,
            )
            if slot_rect.collidepoint(m_x, m_y):
                clicked_card_slot = {"type": "inv", "slot_idx": idx}
                if idx < len(game.player.inventory) and game.player.inventory[idx]:
                    hovered_card = game.player.inventory[idx]
                break

    # Check click handling
    if mouse_clicked:
        if discard_rect.collidepoint(m_x, m_y):
            clicked_trash = True
        elif not clicked_card_slot:
            # Check gun boxes
            for i in range(4):
                x, y = positions[i]
                box_screen_rect = pygame.Rect(x, y, box_w, box_h)
                if box_screen_rect.collidepoint(m_x, m_y):
                    clicked_gun_idx = i
                    break

        # Process actions
        if clicked_trash:
            if game.selected_slot_info:
                # Discard Card
                src = game.selected_slot_info
                if src["type"] == "gun":
                    game.player.weapon_list[src["gun_idx"]].card_list[src["slot_idx"]] = None
                    game.player.weapon_list[src["gun_idx"]]._refresh()
                else:
                    game.player.inventory[src["slot_idx"]] = None
                game.selected_slot_info = None
                game.message_queue.append(["Card discarded", 2.0, (255, 100, 100)])
            elif getattr(game, "selected_gun_slot", None) is not None:
                # Discard Gun
                gun_idx = game.selected_gun_slot
                gun_count = sum(1 for g in game.player.weapon_list if g is not None)
                if gun_count > 1:
                    game.player.weapon_list[gun_idx] = None
                    # Update active weapon if we deleted the current one
                    if game.player.weapon_index == gun_idx:
                        for idx, w in enumerate(game.player.weapon_list):
                            if w is not None:
                                game.player.weapon_index = idx
                                break
                    setattr(game, "selected_gun_slot", None)
                    game.message_queue.append(["Gun discarded", 2.0, (255, 100, 100)])
                else:
                    game.message_queue.append(["Cannot discard your last Gun!", 2.5, (255, 100, 100)])
        elif clicked_card_slot:
            # Deselect gun slot to prevent simultaneous selection
            setattr(game, "selected_gun_slot", None)

            if game.selected_slot_info is None:
                # Select card
                has_card = False
                if clicked_card_slot["type"] == "gun":
                    has_card = (
                        game.player.weapon_list[clicked_card_slot["gun_idx"]].card_list[
                            clicked_card_slot["slot_idx"]
                        ]
                        is not None
                    )
                else:
                    has_card = clicked_card_slot["slot_idx"] < len(game.player.inventory) and game.player.inventory[clicked_card_slot["slot_idx"]] is not None

                if has_card:
                    game.selected_slot_info = clicked_card_slot
            else:
                # Swap or deselect
                if game.selected_slot_info == clicked_card_slot:
                    game.selected_slot_info = None
                else:
                    src = game.selected_slot_info
                    dst = clicked_card_slot

                    if src["type"] == "gun":
                        src_list = game.player.weapon_list[src["gun_idx"]].card_list
                    else:
                        src_list = game.player.inventory

                    if dst["type"] == "gun":
                        dst_list = game.player.weapon_list[dst["gun_idx"]].card_list
                    else:
                        dst_list = game.player.inventory

                    # Perform swap
                    src_list[src["slot_idx"]], dst_list[dst["slot_idx"]] = (
                        dst_list[dst["slot_idx"]],
                        src_list[src["slot_idx"]],
                    )

                    # Refresh guns if needed
                    if src["type"] == "gun":
                        game.player.weapon_list[src["gun_idx"]]._refresh()
                    if dst["type"] == "gun":
                        game.player.weapon_list[dst["gun_idx"]]._refresh()

                    game.selected_slot_info = None

        elif clicked_gun_idx is not None:
            # Deselect card slot to prevent simultaneous selection
            game.selected_slot_info = None

            cur_selected = getattr(game, "selected_gun_slot", None)
            if cur_selected is None:
                if game.player.weapon_list[clicked_gun_idx] is not None:
                    setattr(game, "selected_gun_slot", clicked_gun_idx)
            else:
                if cur_selected != clicked_gun_idx:
                    game.player.weapon_list[cur_selected], game.player.weapon_list[clicked_gun_idx] = (
                        game.player.weapon_list[clicked_gun_idx],
                        game.player.weapon_list[cur_selected],
                    )
                    if game.player.weapon_list[cur_selected]:
                        game.player.weapon_list[cur_selected]._refresh()
                    if game.player.weapon_list[clicked_gun_idx]:
                        game.player.weapon_list[clicked_gun_idx]._refresh()
                setattr(game, "selected_gun_slot", None)

    # Draw the tool tip
    if hovered_card:
        name, info = hovered_card.get_info()

        # Tooltip parameters
        padding = 10
        line_spacing = 4
        max_w = 300

        # Helper for text wrapping
        def get_wrapped_lines(text, font, max_width):
            lines = []
            for paragraph in text.split("\n"):
                words = paragraph.split(" ")
                curr = []
                for w in words:
                    if not w:
                        continue
                    test = " ".join(curr + [w])
                    if font.size(test)[0] <= max_width:
                        curr.append(w)
                    else:
                        lines.append(" ".join(curr))
                        curr = [w]
                lines.append(" ".join(curr))
            return [l for l in lines if l]

        name_surf = game.font.render(name, True, (255, 255, 255))
        wrapped_info = get_wrapped_lines(info, game.HUD_font, max_w - 2 * padding)
        info_surfs = [
            game.HUD_font.render(line, True, (200, 200, 200)) for line in wrapped_info
        ]

        # Calculate total size
        total_h = name_surf.get_height() + padding
        for s in info_surfs:
            total_h += s.get_height() + line_spacing

        total_w = (
            max(name_surf.get_width(), *(s.get_width() for s in info_surfs))
            + 2 * padding
        )
        total_h += padding  # Bottom padding

        # Draw Tooltip Box
        tip_x = m_x + 15
        tip_y = m_y + 15

        # Adjust if off-screen
        if tip_x + total_w > game.screen_width:
            tip_x = m_x - total_w - 5
        if tip_y + total_h > game.screen_height:
            tip_y = m_y - total_h - 5

        tip_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        tip_surf.fill((20, 20, 20, 230))
        pygame.draw.rect(tip_surf, (200, 200, 200), tip_surf.get_rect(), 1)

        # Blit text to tip surface
        curr_y = padding
        tip_surf.blit(name_surf, (padding, curr_y))
        curr_y += name_surf.get_height() + padding // 2
        pygame.draw.line(
            tip_surf, (100, 100, 100), (padding, curr_y), (total_w - padding, curr_y), 1
        )
        curr_y += padding // 2

        for s in info_surfs:
            tip_surf.blit(s, (padding, curr_y))
            curr_y += s.get_height() + line_spacing

        game.screen.blit(tip_surf, (tip_x, tip_y))


def test_screen1(game: "Game", events):
    _ensure_runtime_state(game)

    # ---- 0. Event handling ----
    selected_slot = False
    mouse_clicked = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                game.gun_info = not game.gun_info
            if event.key == pygame.K_m:
                game.map_overview_enabled = not getattr(game, "map_overview_enabled", False)
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                game.player.dash()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game.gun_info:
                selected_slot = True
            else:
                mouse_clicked = True
    # Get current keyboard state (continuous input)
    keys = pygame.key.get_pressed()

    # Get current mouse state
    mouse_buttons = pygame.mouse.get_pressed()

    mouse_pos_world = game.to_world(pygame.mouse.get_pos())
    game.player.mouse_pos_world = mouse_pos_world
    if not game.leveling_up and not game.altar_choosing:
        # ---- 1. World streaming ----
        game.world.ensure_around(game.player.pos2D)

        # ---- 1.5 Bullets update ----
        game.bullet_manager.update(game.delta_time, game.effects_queue)

        # ---- 2. Player ----
        game.player.UpdateWeapon(game.delta_time, mouse_buttons[0], mouse_clicked)
        game.player.Update(game.delta_time, keys)
        game.camera_position = game.player.pos2D

        # Player vs Obstacle collision (spatial grid optimized)
        for obs in Obstacle.get_nearby_obstacles(
            game.player.pos2D, game.spatial_grid_dict
        ):
            if obs.collides_circle(game.player.pos2D, game.player.radius):
                obs.push_out(game.player.pos2D, game.player.radius)

        # Set player's face direction
        diff = pygame.Vector2(mouse_pos_world) - game.player.pos2D
        if diff.length_squared() > 0:
            game.player.face_direction = diff.normalize()

        # ---- 3. Enemies ----
        game.enemy_manager.update(game.delta_time, game.player.pos2D, game.world)
        for e in game.enemy_manager.enemies:
            # Enemy vs Obstacle collision (spatial grid optimized)
            for obs in Obstacle.get_nearby_obstacles(e.pos2D, game.spatial_grid_dict):
                if obs.collides_circle(e.pos2D, e.radius):
                    obs.push_out(e.pos2D, e.radius)

        # ---- 4. Altars ----
        for altar in game.world.altars:
            if altar.update(game.delta_time, game.player.pos2D):
                game.altar_choosing = True
                game.altar_options = list(Altar.BUFF_TYPES)
                game.active_altar = altar
                game.gun_info = False
                break

        # ---- 5. Combat ----
        _handle_player_bullets(game)
        _handle_collisions(game)

        # ---- 6. XP orbs ----
        for orb in list(game.xp_orbs):
            picked = orb.update(game.delta_time, game.player.pos2D)
            if picked:
                leveled = game.player.gain_xp(orb.value)
                game.player.points += orb.value
                if leveled:
                    game.message_queue.append(
                        [f"LEVEL UP!  Lv {game.player.level}", 2.0, (140, 220, 255)]
                    )
                    game.leveling_up = True
                    game.level_up_options = _get_random_cards(game, 3)
                    game.level_up_scroll_offsets = [0, 0, 0]
            if not orb.alive:
                try:
                    game.xp_orbs.remove(orb)
                except ValueError:
                    pass

        # ---- 6.5 Gun pickups ----
        for pickup in list(game.gun_pickups):
            pickup.update(game.delta_time, game)
            if not pickup.alive:
                try:
                    game.gun_pickups.remove(pickup)
                except ValueError:
                    pass

        # ---- 7. Death check ----
        if not game.player.alive:
            game.run_summary = {
                "kills": game.player.kills,
                "time": game.now_time - game.run_start_time,
                "damage": int(game.player.damage_dealt),
                "level": game.player.level,
                "points": game.player.points,
            }
            game.test_screen = 2
            return

        # Periodic cull (every ~2 seconds)
        if game.total_frame_passed % 120 == 0:
            game.world.cull_far(game.player.pos2D)

    # ---- 8. Draw ----
    game.DrawBackground()
    for obs in game.world.obstacles:
        obs.draw(game.screen, game)
    for altar in game.world.altars:
        altar.draw(game.screen, game)
    for orb in game.xp_orbs:
        orb.draw(game.screen, game)
    for pickup in game.gun_pickups:
        pickup.draw(game.screen, game)
    for e in game.enemy_manager.enemies:
        e.draw(game.screen, game)

    game.DrawLayer1()
    _draw_player_invuln_flash(game)
    _draw_effect(game)

    # HUD always on top
    _draw_hud(game)
    _draw_boss_bar(game)
    _draw_messages(game)
    if getattr(game, "map_overview_enabled", False):
        _draw_map_overview(game)

    if game.gun_info:
        _draw_gun_info_overlay(game, events, selected_slot)

    if game.leveling_up:
        _draw_level_up_screen(game, events)
    elif game.altar_choosing:
        _draw_altar_choice_screen(game, events)
