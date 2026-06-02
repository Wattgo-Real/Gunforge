

<<<<<<< Updated upstream
=======
import numpy
>>>>>>> Stashed changes
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Start import Game

from Asset.GameSetting import UI_CONFIG, COLOR_CONFIG, GAME_CONFIG
from Asset.Enemies import EnemyManager
<<<<<<< Updated upstream
from Asset.Pickups import WorldChunkManager, XPOrb
from Asset.Weapons import Card, Gun
=======
from Asset.Pickups import WorldChunkManager, XPOrb, Obstacle, Altar
from Asset.Weapons import Gun, BulletManager
from Asset.SpatialGrid import SpatialGrid, NoneGrid, Quadtree
from Asset.Card import Card
from Asset.Player import Player

>>>>>>> Stashed changes


def _ensure_runtime_state(game: "Game"):
    """Initialize gameplay state once when entering screen 1."""
    if getattr(game, "_screen1_initialised", False):
        return
    game.enemy_manager = EnemyManager()
    game.world = WorldChunkManager(seed=42)
    game.xp_orbs = []
    game.run_start_time = game.now_time
    game.run_summary = None
    game.message_queue = []  # list of [text, timer_left, color]
<<<<<<< Updated upstream
=======
    game.effects_queue = []  # list of [effect : {}, timer_left]
    game.player = Player(position = pygame.Vector2(0,0), radius = 15, color = (0, 150, 255), 
                         bullet_manager = game.bullet_manager)
    game.leveling_up = False
    game.level_up_options = []
    game.level_up_scroll_offsets = [0, 0, 0]
    game.altar_choosing = False
    game.altar_options = []
    game.active_altar = None
>>>>>>> Stashed changes
    game._screen1_initialised = True


def reset_screen1(game: "Game"):
    """Reset gameplay state for a new run. Called by menu / game-over screen."""
    if hasattr(game, "enemy_manager"):
        game.enemy_manager.reset()
    else:
        game.enemy_manager = EnemyManager()
    if hasattr(game, "world"):
        game.world.reset(seed=42)
    else:
        game.world = WorldChunkManager(seed=42)
    game.xp_orbs = []
    game.run_start_time = game.now_time
    game.run_summary = None
    game.message_queue = []
<<<<<<< Updated upstream
    game.player.reset_run(pygame.Vector2(0, 0))
=======
    game.effects_queue = []
    game.leveling_up = False
    game.level_up_options = []
    game.level_up_scroll_offsets = [0, 0, 0]
    game.altar_choosing = False
    game.altar_options = []
    game.active_altar = None
>>>>>>> Stashed changes
    game._screen1_initialised = True


def _drop_boss_reward(game: "Game"):
    for i, slot in enumerate(game.player.weapon_list):
        if slot is None:
            new_info = {
                "cooldown": 0.25,
                "reload": 1.5,
                "scatter_angel": 8,
                "capacity": 30,
                "card_list": [
                    Card(type=0, bullet_type=2),
                    Card(type=1, attribute_modifier_type=1),
                    Card(type=1, attribute_modifier_type=3),
                ],
            }
            game.player.weapon_list[i] = Gun(new_info)
            game.message_queue.append(["BOSS DOWN — new gun acquired!", 5.0, (255, 220, 120)])
            return
    game.message_queue.append(["BOSS DOWN!", 5.0, (255, 220, 120)])


<<<<<<< Updated upstream
=======
def _get_random_cards(game: "Game", count=3):
    """Pick cards based on inverse weights in PROBABILITY_CONFIG."""
    tiers = list(PROBABILITY_CONFIG.keys())
    # weights: higher weight = lower probability (score = 1/weight)
    scores = [1.0 / PROBABILITY_CONFIG[tier]["weight"] for tier in tiers]
    
    selected_cards = []
    for _ in range(count):
        chosen_tier_name = random.choices(tiers, weights=scores, k=1)[0]
        tier_data = PROBABILITY_CONFIG[chosen_tier_name]
        item_config = random.choice(tier_data["items"])
        
        card = Card(
            type=item_config["type"],
            inter_type=item_config["id"]
        )
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
    game.screen.blit(title_text, (game.screen_width // 2 - title_text.get_width() // 2, 80))
    
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
            elif event.button == 4 and hovered_card_idx != -1: # Scroll Up
                game.level_up_scroll_offsets[hovered_card_idx] = max(0, game.level_up_scroll_offsets[hovered_card_idx] - 20)
            elif event.button == 5 and hovered_card_idx != -1: # Scroll Down
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
            words = text.split(' ')
            lines = []
            curr = []
            for ws in words:
                for idx, w in enumerate(ws.split("\n")):
                    if not w: continue
                    test = ' '.join(curr + [w])
                    if font.size(test)[0] <= draw_rect.width and idx == 0:
                        curr.append(w)
                    else:
                        lines.append(' '.join(curr))
                        curr = [w]
            lines.append(' '.join(curr))
            
            total_h = len(lines) * font.get_linesize()
            max_scroll = max(0, total_h - draw_rect.height)
            if game.level_up_scroll_offsets[card_idx] > max_scroll:
                game.level_up_scroll_offsets[card_idx] = max_scroll
            
            old_clip = surface.get_clip()
            surface.set_clip(draw_rect)
            
            line_y = draw_rect.top - game.level_up_scroll_offsets[card_idx]
            for line in lines:
                if not line: continue
                if line_y + font.get_linesize() > draw_rect.top and line_y < draw_rect.bottom:
                    s = font.render(line, True, color)
                    surface.blit(s, (draw_rect.left , line_y))
                line_y += font.get_linesize()
            
            surface.set_clip(old_clip)

        desc_rect = pygame.Rect(x + 20, y + 200, card_w - 40, 160)
        draw_wrapped_text(game.screen, info, game.HUD_font, (230, 230, 230), desc_rect, i)
        
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
        pygame.draw.polygon(surface, color, [
            (end[0] + rect.width * 0.12, end[1] - rect.height * 0.12),
            (end[0] + rect.width * 0.02, end[1] + rect.height * 0.18),
            (end[0] - rect.width * 0.16, end[1] - rect.height * 0.02),
        ])
        pygame.draw.line(surface, (255, 255, 255), start, end, 2)
    elif buff_type == "speed":
        pygame.draw.polygon(surface, color, [
            (cx - rect.width * 0.18, cy - rect.height * 0.28),
            (cx + rect.width * 0.26, cy),
            (cx - rect.width * 0.18, cy + rect.height * 0.28),
        ])
        for offset in (-24, 0, 24):
            pygame.draw.line(surface, (255, 255, 255), (cx - rect.width * 0.38, cy + offset), (cx - rect.width * 0.08, cy + offset), 4)


def _draw_altar_choice_screen(game: "Game", events):
    overlay = pygame.Surface((game.screen_width, game.screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    game.screen.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("Arial", 54, bold=True)
    title_text = title_font.render("ALTAR BLESSING", True, (255, 245, 210))
    game.screen.blit(title_text, (game.screen_width // 2 - title_text.get_width() // 2, 80))

    card_w, card_h = 260, 340
    spacing = 50
    total_w = 3 * card_w + 2 * spacing
    start_x = (game.screen_width - total_w) // 2
    start_y = (game.screen_height - card_h) // 2 + 40

    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = any(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 for event in events)

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
        game.screen.blit(detail_surf, (x + (card_w - detail_surf.get_width()) // 2, y + 240))

        if is_hovered and mouse_clicked:
            game.player.apply_altar_buff(buff_type)
            game.altar_choosing = False
            game.altar_options = []
            game.active_altar = None
            game.message_queue.append([f"Altar: {detail}", 2.5, (255, 230, 120)])
            return


>>>>>>> Stashed changes
def _handle_collisions(game: "Game"):
    player = game.player

    # Bullet vs enemy
    for weapon in player.weapon_list:
        if weapon is None:
            continue
        for bullet in list(weapon.bullets):
            for enemy in game.enemy_manager.enemies:
                if bullet.pos2D.distance_to(enemy.pos2D) < enemy.radius:
                    dmg = bullet.damage * player.damage_multiplier
                    enemy.take_damage(dmg)
                    player.add_damage_dealt(dmg)
                    bullet.triger_hit()
                    if not enemy.alive:
                        game.xp_orbs.append(XPOrb(enemy.pos2D.copy(), value=enemy.xp_drop))
                        player.add_kill()
                        if enemy.is_boss:
                            _drop_boss_reward(game)
                    break

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
    pygame.draw.rect(game.screen, (220, 60, 60), (hp_x, hp_y, int(hp_bar_w * hp_ratio), hp_bar_h))
    pygame.draw.rect(game.screen, (220, 220, 220), (hp_x, hp_y, hp_bar_w, hp_bar_h), 2)
    hp_text = game.HUD_font.render(f"HP {int(player.hp)}/{int(player.max_hp)}", True, (255, 255, 255))
    game.screen.blit(hp_text, (hp_x + 8, hp_y + 3))

    # XP bar (below HP)
    xp_y = hp_y + hp_bar_h + 6
    pygame.draw.rect(game.screen, (30, 30, 30), (hp_x, xp_y, hp_bar_w, 14))
    xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0
    pygame.draw.rect(game.screen, (140, 200, 255), (hp_x, xp_y, int(hp_bar_w * xp_ratio), 14))
    pygame.draw.rect(game.screen, (220, 220, 220), (hp_x, xp_y, hp_bar_w, 14), 1)
    lvl_text = game.HUD_font.render(f"Lv {player.level}  XP {player.xp}/{player.xp_to_next}", True, (240, 240, 240))
    game.screen.blit(lvl_text, (hp_x + 8, xp_y - 2))

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
        boss_text = game.HUD_font.render(f"BOSS in {bm:02d}:{bs:02d}", True, (255, 180, 120))
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
    pygame.draw.rect(game.screen, (200, 30, 30), (bar_x, bar_y, int(bar_w * ratio), bar_h))
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


def _draw_player_invuln_flash(game: "Game"):
    if game.player.invincible_timer > 0:
        screen_pos = game.to_screen(game.player.pos2D)
        flash_alpha = int(120 * (game.player.invincible_timer / GAME_CONFIG["player_invincible_time"]))
        flash_surf = pygame.Surface((game.player.radius * 4, game.player.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(flash_surf, (255, 80, 80, flash_alpha), (game.player.radius * 2, game.player.radius * 2), game.player.radius * 2)
        game.screen.blit(flash_surf, (screen_pos.x - game.player.radius * 2, screen_pos.y - game.player.radius * 2))


def _draw_gun_info_overlay(game: "Game", events, selected_slot: bool):
    """Wattgo's existing gun-info inventory overlay."""
    box_w = UI_CONFIG["gun_box_w"]
    box_h = UI_CONFIG["gun_box_h"]
    slot_size = UI_CONFIG["slot_size"]
    info_x = UI_CONFIG["info_x"]
    pad_x = UI_CONFIG["gun_box_padding_x"]
    pad_y = UI_CONFIG["gun_box_padding_y"]
    spacing_y = UI_CONFIG["gun_box_spacing_y"]

    positions = [
        (pad_x, pad_y), (pad_x, pad_y + spacing_y),
        (game.screen_width - (box_w + pad_x), pad_y), (game.screen_width - (box_w + pad_x), pad_y + spacing_y)
    ]

    for i in range(4):
        x, y = positions[i]
        gun = game.player.weapon_list[i]

        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((30, 30, 30, 180))
        pygame.draw.rect(box_surf, (200, 200, 200, 255), box_surf.get_rect(), 2)

        id_text = game.font.render(str(i + 1), True, (255, 255, 255))
        box_surf.blit(id_text, (10, 5))

        if gun is None:
            empty_text = game.font.render("empty", True, (120, 120, 120))
            text_rect = empty_text.get_rect(center=(box_w // 2, box_h // 2))
            box_surf.blit(empty_text, text_rect)
        else:
            gun_icon_rect = pygame.Rect(40, 70, 100, 100)
            pygame.draw.rect(box_surf, (80, 120, 200), gun_icon_rect)
            pygame.draw.rect(box_surf, (255, 255, 255), gun_icon_rect, 2)

            inner_info_x = 200
            info_y = 15
            stats = {
                "Cooldown": round(gun.cooldown, 2),
                "Reload": round(gun.reload, 2),
                "Scatter": round(gun.scatter_angel, 2),
                "Capacity": f"{gun.capacity_left}/{gun.capacity}"
            }
            for j, (key, value) in enumerate(stats.items()):
                color = COLOR_CONFIG.get(key.lower().replace("scatter", "scatter_angel"), (255, 255, 255))
                if key == "Cooldown": color = COLOR_CONFIG["cooldown"]
                elif key == "Reload": color = COLOR_CONFIG["reload"]
                elif key == "Scatter": color = COLOR_CONFIG["scatter_angel"]
                elif key == "Capacity": color = COLOR_CONFIG["capacity"]
                stat_text = game.HUD_font.render(f"{key}: {value}", True, color)
                box_surf.blit(stat_text, (inner_info_x, info_y + j * 22))

            bar_x = 400
            bar_w, bar_h = 180, 12
            cd_ratio = 1 - (gun.cooldown_timer / gun.cooldown) if gun.cooldown > 0 else 1
            pygame.draw.rect(box_surf, (40, 40, 40), (bar_x, info_y, bar_w, bar_h))
            pygame.draw.rect(box_surf, COLOR_CONFIG["cooldown"], (bar_x, info_y, int(bar_w * cd_ratio), bar_h))
            pygame.draw.rect(box_surf, (200, 200, 200), (bar_x, info_y, bar_w, bar_h), 1)

            rl_ratio = 1 - (gun.reload_timer / gun.reload) if gun.reload > 0 else 1
            pygame.draw.rect(box_surf, (40, 40, 40), (bar_x, info_y + 22, bar_w, bar_h))
            pygame.draw.rect(box_surf, COLOR_CONFIG["reload"], (bar_x, info_y + 22, int(bar_w * rl_ratio), bar_h))
            pygame.draw.rect(box_surf, (200, 200, 200), (bar_x, info_y + 22, bar_w, bar_h), 1)

            pygame.draw.line(box_surf, (255, 255, 255), (0, 30), (inner_info_x - 20, 30), 2)
            pygame.draw.line(box_surf, (255, 255, 255), (inner_info_x - 20, 0), (inner_info_x - 20, box_h), 4)

            slots_total_w = 10 * slot_size
            slots_start_x = inner_info_x
            slots_y = box_h - 2 * slot_size - 15

            for s in range(gun.card_max_slots):
                slot_rect = pygame.Rect(slots_start_x + (s % 10) * slot_size, slots_y + (s // 10) * slot_size, slot_size, slot_size)
                pygame.draw.rect(box_surf, (150, 150, 150), slot_rect, 1)

                if game.selected_slot_info and game.selected_slot_info['type'] == 'gun' and game.selected_slot_info['gun_idx'] == i and game.selected_slot_info['slot_idx'] == s:
                    pygame.draw.rect(box_surf, (255, 255, 100), slot_rect, 3)

                card = gun.card_list[s]
                if card:
                    card.draw(box_surf, slot_rect)

        game.screen.blit(box_surf, (x, y))

    # Inventory grid
    grid_cell_size = UI_CONFIG["grid_cell_size"]
    grid_cols = UI_CONFIG["grid_cols"]
    grid_rows = UI_CONFIG["grid_rows"]
    grid_w = grid_cols * grid_cell_size
    grid_h = grid_rows * grid_cell_size

    grid_start_x = (game.screen_width - grid_w) // 2
    grid_start_y = game.screen_height - grid_h - UI_CONFIG["inv_bottom_padding"]

    grid_surface = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    for r in range(grid_rows):
        for c in range(grid_cols):
            idx = r * grid_cols + c
            rect = pygame.Rect(c * grid_cell_size, r * grid_cell_size, grid_cell_size, grid_cell_size)
            pygame.draw.rect(grid_surface, (200, 200, 200, 200), rect, 1)

            if game.selected_slot_info and game.selected_slot_info['type'] == 'inv' and game.selected_slot_info['slot_idx'] == idx:
                pygame.draw.rect(grid_surface, (255, 255, 100), rect, 3)

            if idx < len(game.player.inventory):
                card = game.player.inventory[idx]
                if card:
                    card.draw(grid_surface, rect)

    game.screen.blit(grid_surface, (grid_start_x, grid_start_y))

    # Tooltip + click handling
    m_x, m_y = pygame.mouse.get_pos()
    clicked_slot = None
    hovered_card = None

    for i in range(4):
        gun = game.player.weapon_list[i]
        if not gun:
            continue
        gx, gy = positions[i]
        slots_start_x = gx + UI_CONFIG["info_x"]
        slots_start_y = gy + box_h - 2 * slot_size - 15
        for s in range(gun.card_max_slots):
            slot_rect = pygame.Rect(slots_start_x + (s % 10) * slot_size, slots_start_y + (s // 10) * slot_size, slot_size, slot_size)
            if slot_rect.collidepoint(m_x, m_y):
                clicked_slot = {'type': 'gun', 'gun_idx': i, 'slot_idx': s}
                if gun.card_list[s]:
                    hovered_card = gun.card_list[s]
                break
        if hovered_card:
            break

    if not hovered_card:
        inv_start_x = grid_start_x
        inv_start_y = grid_start_y
        for idx in range(40):
            r, c = idx // grid_cols, idx % grid_cols
            slot_rect = pygame.Rect(inv_start_x + c * grid_cell_size, inv_start_y + r * grid_cell_size, grid_cell_size, grid_cell_size)
            if slot_rect.collidepoint(m_x, m_y):
                clicked_slot = {'type': 'inv', 'slot_idx': idx}
                if idx < len(game.player.inventory) and game.player.inventory[idx]:
                    hovered_card = game.player.inventory[idx]
                break

    if clicked_slot and selected_slot:
        if game.selected_slot_info is None:
            has_card = False
            if clicked_slot['type'] == 'gun':
                has_card = game.player.weapon_list[clicked_slot['gun_idx']].card_list[clicked_slot['slot_idx']] is not None
            else:
                has_card = game.player.inventory[clicked_slot['slot_idx']] is not None
            if has_card:
                game.selected_slot_info = clicked_slot
        else:
            if game.selected_slot_info == clicked_slot:
                game.selected_slot_info = None
            else:
                src = game.selected_slot_info
                dst = clicked_slot
                src_list = game.player.weapon_list[src['gun_idx']].card_list if src['type'] == 'gun' else game.player.inventory
                dst_list = game.player.weapon_list[dst['gun_idx']].card_list if dst['type'] == 'gun' else game.player.inventory
                src_list[src['slot_idx']], dst_list[dst['slot_idx']] = dst_list[dst['slot_idx']], src_list[src['slot_idx']]
                if src['type'] == 'gun':
                    game.player.weapon_list[src['gun_idx']]._refresh()
                if dst['type'] == 'gun':
                    game.player.weapon_list[dst['gun_idx']]._refresh()
                game.selected_slot_info = None

    if hovered_card:
        name, info = hovered_card.get_info()
        padding = 10
        line_spacing = 4
        max_w = 300

        def get_wrapped_lines(text, font, max_width):
            lines = []
            for paragraph in text.split('\n'):
                words = paragraph.split(' ')
                curr = []
                for w in words:
                    if not w:
                        continue
                    test = ' '.join(curr + [w])
                    if font.size(test)[0] <= max_width:
                        curr.append(w)
                    else:
                        lines.append(' '.join(curr))
                        curr = [w]
                lines.append(' '.join(curr))
            return [l for l in lines if l]

        name_surf = game.font.render(name, True, (255, 255, 255))
        wrapped_info = get_wrapped_lines(info, game.HUD_font, max_w - 2 * padding)
        info_surfs = [game.HUD_font.render(line, True, (200, 200, 200)) for line in wrapped_info]
        total_h = name_surf.get_height() + padding
        for s in info_surfs:
            total_h += s.get_height() + line_spacing
        total_w = max(name_surf.get_width(), *(s.get_width() for s in info_surfs)) + 2 * padding
        total_h += padding

        tip_x = m_x + 15
        tip_y = m_y + 15
        if tip_x + total_w > game.screen_width:
            tip_x = m_x - total_w - 5
        if tip_y + total_h > game.screen_height:
            tip_y = m_y - total_h - 5

        tip_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
        tip_surf.fill((20, 20, 20, 230))
        pygame.draw.rect(tip_surf, (200, 200, 200), tip_surf.get_rect(), 1)

        curr_y = padding
        tip_surf.blit(name_surf, (padding, curr_y))
        curr_y += name_surf.get_height() + padding // 2
        pygame.draw.line(tip_surf, (100, 100, 100), (padding, curr_y), (total_w - padding, curr_y), 1)
        curr_y += padding // 2

        for s in info_surfs:
            tip_surf.blit(s, (padding, curr_y))
            curr_y += s.get_height() + line_spacing

        game.screen.blit(tip_surf, (tip_x, tip_y))


def test_screen1(game: "Game", events):
    _ensure_runtime_state(game)

    # ---- 0. Event handling ----
    selected_slot = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                game.gun_info = not game.gun_info
        if game.gun_info and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selected_slot = True

    mouse_pos_world = game.to_world(pygame.mouse.get_pos())
<<<<<<< Updated upstream
    diff = pygame.Vector2(mouse_pos_world) - game.player.pos2D
    if diff.length_squared() > 0:
        game.player.face_direction = diff.normalize()
=======
    if not game.leveling_up and not game.altar_choosing:
        # ---- 1. World streaming ----
        game.world.ensure_around(game.player.pos2D)
>>>>>>> Stashed changes

    # ---- 1. World streaming ----
    game.world.ensure_around(game.player.pos2D)

    # ---- 2. Player ----
    game.PlayerUpdate()
    game.player.update_timers(game.delta_time)
    for obs in game.world.obstacles:
        if obs.collides_circle(game.player.pos2D, game.player.radius):
            obs.push_out(game.player.pos2D, game.player.radius)

    # ---- 3. Enemies ----
    game.enemy_manager.update(game.delta_time, game.player.pos2D)
    for e in game.enemy_manager.enemies:
        for obs in game.world.obstacles:
            if obs.collides_circle(e.pos2D, e.radius):
                obs.push_out(e.pos2D, e.radius)

    # ---- 4. Altars ----
    for altar in game.world.altars:
        result = altar.update(game.delta_time, game.player.pos2D)
        if result:
            game.player.apply_altar_buff(result)
            label = {"hp": "+25 MAX HP", "damage": "+15% DAMAGE", "speed": "+30 SPEED"}.get(result, result)
            game.message_queue.append([f"Altar: {label}", 2.5, (255, 230, 120)])

<<<<<<< Updated upstream
    # ---- 5. Combat ----
    _handle_collisions(game)
=======
        # ---- 4. Altars ----
        for altar in game.world.altars:
            if altar.update(game.delta_time, game.player.pos2D):
                game.altar_choosing = True
                game.altar_options = list(Altar.BUFF_TYPES)
                game.active_altar = altar
                game.gun_info = False
                break
>>>>>>> Stashed changes

    # ---- 6. XP orbs ----
    for orb in list(game.xp_orbs):
        picked = orb.update(game.delta_time, game.player.pos2D)
        if picked:
            leveled = game.player.gain_xp(orb.value)
            game.player.points += orb.value
            if leveled:
                game.message_queue.append([f"LEVEL UP!  Lv {game.player.level}", 2.0, (140, 220, 255)])
        if not orb.alive:
            try:
                game.xp_orbs.remove(orb)
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
    for e in game.enemy_manager.enemies:
        e.draw(game.screen, game)

    game.DrawLayer1()
    _draw_player_invuln_flash(game)

    # HUD always on top
    _draw_hud(game)
    _draw_boss_bar(game)
    _draw_messages(game)

    if game.gun_info:
        _draw_gun_info_overlay(game, events, selected_slot)
<<<<<<< Updated upstream
=======

    if game.leveling_up:
        _draw_level_up_screen(game, events)
    elif game.altar_choosing:
        _draw_altar_choice_screen(game, events)
>>>>>>> Stashed changes
