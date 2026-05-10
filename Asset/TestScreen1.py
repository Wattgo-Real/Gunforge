

import numpy
from turtle import position
import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Start import Game

from Asset.GameSetting import UI_CONFIG, COLOR_CONFIG, GAME_CONFIG, GRID_CONFIG
from Asset.GameSetting import ENTITY_TYPE
from Asset.Enemies import EnemyManager
from Asset.Pickups import WorldChunkManager, XPOrb
from Asset.Weapons import Gun
from Asset.Card import Card
from Asset.Player import Player



def _ensure_runtime_state(game: "Game"):
    """Initialize gameplay state once when entering screen 1."""
    if getattr(game, "_screen1_initialised", False):
        return
    game.spatial_grid_dict = {i : {} for i in range(GRID_CONFIG["number_of_cells_w"] * GRID_CONFIG["number_of_cells_h"])}
    game.enemy_manager = EnemyManager(spatial_grid_dict_pointer = game.spatial_grid_dict)
    game.world = WorldChunkManager(seed=42)
    game.xp_orbs = []
    game.run_start_time = game.now_time
    game.run_summary = None
    game.message_queue = []  # list of [text, timer_left, color]
    game.effects_queue = []  # list of [effect : {}, timer_left]
    game.player = Player(position = pygame.Vector2(0,0), radius = 15, color = (0, 150, 255), spatial_grid_dict = game.spatial_grid_dict)
    game._screen1_initialised = True


def reset_screen1(game: "Game"):
    """Reset gameplay state for a new run. Called by menu / game-over screen."""
    if  hasattr(game, "spatial_grid_dict"):
        for cell_key in game.spatial_grid_dict.keys():
            game.spatial_grid_dict[cell_key].clear()
    else:
        game.spatial_grid_dict = {i : {} for i in range(GRID_CONFIG["number_of_cells_w"] * GRID_CONFIG["number_of_cells_h"])}
    if hasattr(game, "enemy_manager"):
        game.enemy_manager.reset()
    else:
        game.enemy_manager = EnemyManager(spatial_grid_dict_pointer = game.spatial_grid_dict)
    if hasattr(game, "world"):
        game.world.reset(seed=42)
    else:
        game.world = WorldChunkManager(seed=42)
    
    if hasattr(game, "player"):
        game.player.reset_run(pygame.Vector2(0, 0))
    else:
        game.player = Player(position = pygame.Vector2(0,0), radius = 15, color = (0, 150, 255), spatial_grid_dict = game.spatial_grid_dict)

    game.xp_orbs = []
    game.run_start_time = game.now_time
    game.run_summary = None
    game.message_queue = []
    game.effects_queue = []
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
        e1_grid_x = int(e1.pos2D.x / GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]
        e1_grid_y = int(e1.pos2D.y / GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]
        
        for i in range(e1_grid_x - 1, e1_grid_x + 2):
            for j in range(e1_grid_y - 1, e1_grid_y + 2):
                e2_grid_x = i % GRID_CONFIG["number_of_cells_w"]
                e2_grid_y = j % GRID_CONFIG["number_of_cells_h"]
                grid_pos = e2_grid_x + e2_grid_y * GRID_CONFIG["number_of_cells_w"]
                for e2 in game.spatial_grid_dict[grid_pos].values():
                    if e2.entity_type != ENTITY_TYPE["enemy"] or e1.uuid == e2.uuid:
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

    # Bullet vs enemy
    # num_of_bullet = 0
    # num_of_calculate = 0
    for weapon in player.weapon_list:
        if weapon is None:
            continue
        for bullet in list(weapon.bullets):
            # num_of_bullet += 1
            # Spatial Partition Grid is used to find the nearest enemy in the area around the bullet.
            bullet_grid_pos = [int(bullet.pos2D.x / GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"],
                               int(bullet.pos2D.y / GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]]
            for i in range(bullet_grid_pos[0] - 1, bullet_grid_pos[0] + 2):
                for j in range(bullet_grid_pos[1] - 1, bullet_grid_pos[1] + 2):
                    grid_x = i % GRID_CONFIG["number_of_cells_w"]
                    grid_y = j % GRID_CONFIG["number_of_cells_h"]
                    grid_pos = grid_x + grid_y * GRID_CONFIG["number_of_cells_w"]
                    for entity in game.spatial_grid_dict[grid_pos].values():
                        if entity.entity_type != ENTITY_TYPE["enemy"]:
                            continue
                        #num_of_calculate += 1
                        if entity.pos2D.distance_to(bullet.pos2D) < bullet.radius + entity.radius + 5:
                            bullet.triger_hit(player, entity, effect_queue = game.effects_queue, spatial_grid_dict = game.spatial_grid_dict)
                            if not entity.alive:
                                game.xp_orbs.append(XPOrb(entity.pos2D.copy(), value=entity.xp_drop))
                                player.add_kill()
                                if entity.is_boss:
                                    _drop_boss_reward(game)
                            break

            '''
            v2
            for enemy in game.enemy_manager.enemies:
                num_of_calculate += 1
                if bullet.pos2D.distance_to(enemy.pos2D) < enemy.radius + 5: # Small buffer
                    bullet.triger_hit(player, enemy, effect_queue = game.effects_queue, spatial_grid_dict = game.spatial_grid_dict)
                    if not enemy.alive:
                        game.xp_orbs.append(XPOrb(enemy.pos2D.copy(), value=enemy.xp_drop))
                        player.add_kill()
                        if enemy.is_boss:
                            _drop_boss_reward(game)
                    break
            
            v1
            for enemy in game.enemy_manager.enemies:
                if bullet.pos2D.distance_to(enemy.pos2D) < enemy.radius:
                    dmg = (bullet.damage()) * player.damage_multiplier
                    enemy.take_damage(dmg)
                    player.add_damage_dealt(dmg)
                    bullet.triger_hit()
                    if not enemy.alive:
                        game.xp_orbs.append(XPOrb(enemy.pos2D.copy(), value=enemy.xp_drop))
                        player.add_kill()
                        if enemy.is_boss:
                            _drop_boss_reward(game)
                    break
            '''

    #print("num of bullet = ", num_of_bullet, "num of enemies = ", len(game.enemy_manager.enemies), "num of calculate", num_of_calculate)


    # lifetime of the Bullets 
    for weapon in player.weapon_list:
        if weapon is None:
            continue
        for bullet in list(weapon.bullets):
            if bullet.timer > bullet.lifetime:
                bullet.triger_lifetime(player, effect_queue = game.effects_queue, spatial_grid_dict = game.spatial_grid_dict)


def _draw_effect(game: "Game"):
    for effect in game.effects_queue:
        effect[1] -= game.delta_time
        effect_info = effect[0]

        time_left = effect[1]
        if time_left <= 0:
            game.effects_queue.remove(effect)
            continue

        if 'disappearing_circle' in effect_info:
            for info in effect_info['disappearing_circle']:
                color = info['color']
                alpha = int(color[3] * (time_left / info['total_time']))
                position = info['pos_2D']
                position = game.to_screen(position)
                radius = info['radius']
                effect_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(effect_surf, (color[0], color[1], color[2], alpha), (radius, radius), radius)
                game.screen.blit(effect_surf, (position.x - radius, position.y - radius))


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
    xp_bar_h = 14
    pygame.draw.rect(game.screen, (30, 30, 30), (hp_x, xp_y, hp_bar_w, xp_bar_h))
    xp_ratio = player.xp / player.xp_to_next if player.xp_to_next > 0 else 0
    pygame.draw.rect(game.screen, (140, 200, 255), (hp_x, xp_y, int(hp_bar_w * xp_ratio), xp_bar_h))
    pygame.draw.rect(game.screen, (220, 220, 220), (hp_x, xp_y, hp_bar_w, xp_bar_h), 1)
    lvl_text = game.HUD_font.render(f"Lv {player.level}  XP {player.xp}/{player.xp_to_next}", True, (240, 240, 240))
    game.screen.blit(lvl_text, (hp_x + 8, xp_y - 2))

    # Dash Cooldown (below XP)
    dash_bar_y = xp_y + xp_bar_h + 6
    dash_bar_h = 6
    pygame.draw.rect(game.screen, (30, 30, 30), (hp_x, dash_bar_y, hp_bar_w, dash_bar_h))
    if player.dash_cooldown_timer > 0:
        dash_ratio = 1.0 - (player.dash_cooldown_timer / player.dash_cooldown)
        pygame.draw.rect(game.screen, (100, 100, 100), (hp_x, dash_bar_y, int(hp_bar_w * dash_ratio), dash_bar_h))
    else:
        pygame.draw.rect(game.screen, (100, 255, 100), (hp_x, dash_bar_y, hp_bar_w, dash_bar_h))
    pygame.draw.rect(game.screen, (220, 220, 220), (hp_x, dash_bar_y, hp_bar_w, dash_bar_h), 1)

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
    bar_w = game.screen_width - 200
    bar_h = 24
    bar_x = 100
    bar_y = game.screen_height - bar_h - 30
    pygame.draw.rect(game.screen, (40, 0, 0), (bar_x, bar_y, bar_w, bar_h))
    ratio = max(0.0, boss.hp / boss.max_hp)
    pygame.draw.rect(game.screen, (200, 30, 30), (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(game.screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2)
    label = game.font.render("BOSS", True, (255, 255, 255))
    game.screen.blit(label, (bar_x + 10, bar_y - 4))


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

    # --- Draw Gun Boxes ---
    for i in range(4):
        x, y = positions[i]
        gun = game.player.weapon_list[i]
        
        # Create box surface
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((30, 30, 30, 180)) # Semi-transparent dark gray
        pygame.draw.rect(box_surf, (200, 200, 200, 255), box_surf.get_rect(), 2) # Border
        
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
            pygame.draw.rect(box_surf, (80, 120, 200), gun_icon_rect) # Placeholder color
            pygame.draw.rect(box_surf, (255, 255, 255), gun_icon_rect, 2)
            
            # 3. Gun Information (top-right)
            info_x = 200
            info_y = 15
            stats = {
                "Cooldown" : round(gun.cooldown, 2),
                "Reload" : round(gun.reload, 2),
                "Scatter" : round(gun.scatter_angel, 2),
                "Capacity" : f"{gun.capacity_left}/{gun.capacity}"
            }
            for j, (key, value) in enumerate(stats.items()):
                if key == "Cooldown":
                    color = COLOR_CONFIG["cooldown"]
                elif key == "Reload":
                    color = COLOR_CONFIG["reload"]
                elif key == "Scatter":
                    color = COLOR_CONFIG["scatter_angel"]
                elif key == "Capacity":
                    color = COLOR_CONFIG["capacity"]

                stat_text = game.HUD_font.render(f"{key}: {value}", True, color)
                box_surf.blit(stat_text, (info_x, info_y + j * 22))

            # 3.5. Cooldown & Reload Bars
            bar_x = 400
            bar_w, bar_h = 180, 12
            
            # Cooldown Bar
            cd_ratio = 1 - (gun.cooldown_timer / gun.cooldown) if gun.cooldown > 0 else 1
            pygame.draw.rect(box_surf, (40, 40, 40), (bar_x, info_y, bar_w, bar_h)) # BG
            pygame.draw.rect(box_surf, COLOR_CONFIG["cooldown"], (bar_x, info_y, int(bar_w * cd_ratio), bar_h)) # Fill
            pygame.draw.rect(box_surf, (200, 200, 200), (bar_x, info_y, bar_w, bar_h), 1) # Border

            # Reload Bar
            rl_ratio = 1 - (gun.reload_timer / gun.reload) if gun.reload > 0 else 1
            pygame.draw.rect(box_surf, (40, 40, 40), (bar_x, info_y + 22, bar_w, bar_h)) # BG
            pygame.draw.rect(box_surf, COLOR_CONFIG["reload"], (bar_x, info_y + 22, int(bar_w * rl_ratio), bar_h)) # Fill
            pygame.draw.rect(box_surf, (200, 200, 200), (bar_x, info_y + 22, bar_w, bar_h), 1) # Border

            pygame.draw.line(box_surf, (255, 255, 255), (0, 30), (info_x - 20, 30), 2)
            pygame.draw.line(box_surf, (255, 255, 255), (info_x - 20, 0), (info_x - 20, box_h), 4)

            # Hover Detection & Slot Drawing
            m_x, m_y = pygame.mouse.get_pos()
            
            # 4. Card Max Slots (bottom-right)
            slots_total_w = 10 * slot_size
            slots_start_x = info_x
            slots_y = box_h - 2 * slot_size - 15
            
            for s in range(gun.card_max_slots):
                slot_rect = pygame.Rect(slots_start_x + (s % 10) * slot_size, slots_y + (s//10) * slot_size, slot_size, slot_size)
                pygame.draw.rect(box_surf, (150, 150, 150), slot_rect, 1)

                # Draw selection highlight
                if game.selected_slot_info and game.selected_slot_info['type'] == 'gun' and game.selected_slot_info['gun_idx'] == i and game.selected_slot_info['slot_idx'] == s:
                    pygame.draw.rect(box_surf, (255, 255, 100), slot_rect, 3)

                # Draw card icon if exists
                card = gun.card_list[s]
                if card:
                    card.draw(box_surf, slot_rect)

        # Blit box to screen
        game.screen.blit(box_surf, (x, y))



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
            rect = pygame.Rect(c * grid_cell_size, r * grid_cell_size, grid_cell_size, grid_cell_size)
            pygame.draw.rect(grid_surface, (200, 200, 200, 200), rect, 1)
            
            # Draw selection highlight
            if game.selected_slot_info and game.selected_slot_info['type'] == 'inv' and game.selected_slot_info['slot_idx'] == idx:
                pygame.draw.rect(grid_surface, (255, 255, 100), rect, 3)

            # Draw card icon
            if idx < len(game.player.inventory):
                card = game.player.inventory[idx]
                if card:
                    card.draw(grid_surface, rect)
    
    game.screen.blit(grid_surface, (grid_start_x, grid_start_y))

    # --- Draw Tooltip and clicked slot ---
    m_x, m_y = pygame.mouse.get_pos()
    clicked_slot = None
    hovered_card = None

    # Check Gun Slots for hover or check clicked slot
    for i in range(4):
        gun = game.player.weapon_list[i]
        if not gun: continue
        gx, gy = positions[i]
        slots_start_x = gx + info_x
        slots_start_y = gy + box_h - 2 * slot_size - 15
        for s in range(gun.card_max_slots):
            slot_rect = pygame.Rect(slots_start_x + (s % 10) * slot_size, slots_start_y + (s // 10) * slot_size, slot_size, slot_size)
            if slot_rect.collidepoint(m_x, m_y):
                clicked_slot = {'type': 'gun', 'gun_idx': i, 'slot_idx': s}
                if gun.card_list[s]:
                    hovered_card = gun.card_list[s]
                break
        if hovered_card: break

    # Check Inventory for hover or check clicked slot
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

    # Move the card from the selected sol to the clicked slot.
    if clicked_slot and selected_slot:
        if game.selected_slot_info is None:
            # Select if there is a card
            has_card = False
            if clicked_slot['type'] == 'gun':
                has_card = game.player.weapon_list[clicked_slot['gun_idx']].card_list[clicked_slot['slot_idx']] is not None
            else:
                has_card = game.player.inventory[clicked_slot['slot_idx']] is not None
            
            if has_card:
                game.selected_slot_info = clicked_slot
        else:
            # Already selected, try to move/swap
            if game.selected_slot_info == clicked_slot:
                game.selected_slot_info = None
            else:
                # Perform swap
                # Get source card
                src = game.selected_slot_info
                dst = clicked_slot
                
                if src['type'] == 'gun':
                    src_list = game.player.weapon_list[src['gun_idx']].card_list
                else:
                    src_list = game.player.inventory
                
                if dst['type'] == 'gun':
                    dst_list = game.player.weapon_list[dst['gun_idx']].card_list
                else:
                    dst_list = game.player.inventory
                
                # Swap
                src_list[src['slot_idx']], dst_list[dst['slot_idx']] = dst_list[dst['slot_idx']], src_list[src['slot_idx']]
                
                # Refresh guns if needed
                if src['type'] == 'gun': game.player.weapon_list[src['gun_idx']]._refresh()
                if dst['type'] == 'gun': game.player.weapon_list[dst['gun_idx']]._refresh()
                
                game.selected_slot_info = None

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
            for paragraph in text.split('\n'):
                words = paragraph.split(' ')
                curr = []
                for w in words:
                    if not w: continue
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
        
        # Calculate total size
        total_h = name_surf.get_height() + padding
        for s in info_surfs:
            total_h += s.get_height() + line_spacing
        
        total_w = max(name_surf.get_width(), *(s.get_width() for s in info_surfs)) + 2 * padding
        total_h += padding # Bottom padding
        
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
    mouse_clicked = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                game.gun_info = not game.gun_info
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                game.player.dash()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game.gun_info:
                selected_slot = True
            else:
                mouse_clicked = True

    mouse_pos_world = game.to_world(pygame.mouse.get_pos())
    diff = pygame.Vector2(mouse_pos_world) - game.player.pos2D
    if diff.length_squared() > 0:
        game.player.face_direction = diff.normalize()

    # ---- 1. World streaming ----
    game.world.ensure_around(game.player.pos2D)

    # ---- 2. Player ----
    game.PlayerUpdate(mouse_clicked)
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
    _draw_effect(game)

    # HUD always on top
    _draw_hud(game)
    _draw_boss_bar(game)
    _draw_messages(game)

    if game.gun_info:
        _draw_gun_info_overlay(game, events, selected_slot)
