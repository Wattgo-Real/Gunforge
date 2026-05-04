

import pygame

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Start import Game

from Asset.GameSetting import UI_CONFIG, COLOR_CONFIG
from Asset.Player import Enemy

# 可以在裡面測試不同項目，目前使用當中: Wattgo
def test_screen1(self : "Game", events):
    # --- 0.5 Init Enemy ---
    if not hasattr(self, 'enemy'):
        self.enemy = Enemy(pygame.Vector2(300, 300), hp=10000)
    # --- 0. Event Handling ---
    m_x, m_y = pygame.mouse.get_pos()
    selected_slot = False
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.gun_info = not self.gun_info
        
        if self.gun_info and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            selected_slot = True


    mouse_pos_world = self.to_world(pygame.mouse.get_pos())
    self.player.face_direction = (pygame.Vector2(mouse_pos_world) - self.player.pos2D).normalize()

    # --- 1. Player Movement & Weapon Update. ---
    self.PlayerUpdate()
    
    # --- 1.5 Enemy Update & Collision ---
    self.enemy.update(self.delta_time)
    for weapon in self.player.weapon_list:
        if weapon is None: continue
        for bullet in weapon.bullets:
            if bullet.pos2D.distance_to(self.enemy.pos2D) < self.enemy.radius:
                self.enemy.take_damage(bullet.damage)
                bullet.triger_hit()

    # --- 2. Draw background. ---
    # Draw the background.
    self.DrawBackground()

    # --- 3. Draw player, bullet, weapon, enemy. ---
    self.enemy.draw(self.screen, self)
    self.DrawLayer1()

    # --- 4. Gun Info UI ---
    if self.gun_info:
        # UI Config Values
        box_w = UI_CONFIG["gun_box_w"]
        box_h = UI_CONFIG["gun_box_h"]
        slot_size = UI_CONFIG["slot_size"]
        info_x = UI_CONFIG["info_x"]
        pad_x = UI_CONFIG["gun_box_padding_x"]
        pad_y = UI_CONFIG["gun_box_padding_y"]
        spacing_y = UI_CONFIG["gun_box_spacing_y"]
        
        positions = [
            (pad_x, pad_y), (pad_x, pad_y + spacing_y),
            (self.screen_width - (box_w + pad_x), pad_y), (self.screen_width - (box_w + pad_x), pad_y + spacing_y)
        ]

        # --- Draw Gun Boxes ---
        for i in range(4):
            x, y = positions[i]
            gun = self.player.weapon_list[i]
            
            # Create box surface
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box_surf.fill((30, 30, 30, 180)) # Semi-transparent dark gray
            pygame.draw.rect(box_surf, (200, 200, 200, 255), box_surf.get_rect(), 2) # Border
            
            # 1. ID Number (top-left)
            id_text = self.font.render(str(i + 1), True, (255, 255, 255))
            box_surf.blit(id_text, (10, 5))

        
            if gun is None:
                # Display "empty" in center
                empty_text = self.font.render("empty", True, (120, 120, 120))
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

                    stat_text = self.HUD_font.render(f"{key}: {value}", True, color)
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
                    if self.selected_slot_info and self.selected_slot_info['type'] == 'gun' and self.selected_slot_info['gun_idx'] == i and self.selected_slot_info['slot_idx'] == s:
                        pygame.draw.rect(box_surf, (255, 255, 100), slot_rect, 3)

                    # Draw card icon if exists
                    card = gun.card_list[s]
                    if card:
                        card.draw(box_surf, slot_rect)

            # Blit box to screen
            self.screen.blit(box_surf, (x, y))



        # --- Draw Inventory Grid ---
        grid_cell_size = UI_CONFIG["grid_cell_size"]
        grid_cols = UI_CONFIG["grid_cols"]
        grid_rows = UI_CONFIG["grid_rows"]
        grid_w = grid_cols * grid_cell_size
        grid_h = grid_rows * grid_cell_size
        
        grid_start_x = (self.screen_width - grid_w) // 2
        grid_start_y = self.screen_height - grid_h - UI_CONFIG["inv_bottom_padding"]
        
        grid_surface = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
        # grid_surface.fill((20, 20, 20, 100)) # Optional background
        for r in range(grid_rows):
            for c in range(grid_cols):
                idx = r * grid_cols + c
                rect = pygame.Rect(c * grid_cell_size, r * grid_cell_size, grid_cell_size, grid_cell_size)
                pygame.draw.rect(grid_surface, (200, 200, 200, 200), rect, 1)
                
                # Draw selection highlight
                if self.selected_slot_info and self.selected_slot_info['type'] == 'inv' and self.selected_slot_info['slot_idx'] == idx:
                    pygame.draw.rect(grid_surface, (255, 255, 100), rect, 3)

                # Draw card icon
                if idx < len(self.player.inventory):
                    card = self.player.inventory[idx]
                    if card:
                        card.draw(grid_surface, rect)
        
        self.screen.blit(grid_surface, (grid_start_x, grid_start_y))

        # --- Draw Tooltip and clicked slot ---
        m_x, m_y = pygame.mouse.get_pos()
        clicked_slot = None
        hovered_card = None

        # Check Gun Slots for hover or check clicked slot
        for i in range(4):
            gun = self.player.weapon_list[i]
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
                    if idx < len(self.player.inventory) and self.player.inventory[idx]:
                        hovered_card = self.player.inventory[idx]
                    break

        # Move the card from the selected sol to the clicked slot.
        if clicked_slot and selected_slot:
            if self.selected_slot_info is None:
                # Select if there is a card
                has_card = False
                if clicked_slot['type'] == 'gun':
                    has_card = self.player.weapon_list[clicked_slot['gun_idx']].card_list[clicked_slot['slot_idx']] is not None
                else:
                    has_card = self.player.inventory[clicked_slot['slot_idx']] is not None
                
                if has_card:
                    self.selected_slot_info = clicked_slot
            else:
                # Already selected, try to move/swap
                if self.selected_slot_info == clicked_slot:
                    self.selected_slot_info = None
                else:
                    # Perform swap
                    # Get source card
                    src = self.selected_slot_info
                    dst = clicked_slot
                    
                    if src['type'] == 'gun':
                        src_list = self.player.weapon_list[src['gun_idx']].card_list
                    else:
                        src_list = self.player.inventory
                    
                    if dst['type'] == 'gun':
                        dst_list = self.player.weapon_list[dst['gun_idx']].card_list
                    else:
                        dst_list = self.player.inventory
                    
                    # Swap
                    src_list[src['slot_idx']], dst_list[dst['slot_idx']] = dst_list[dst['slot_idx']], src_list[src['slot_idx']]
                    
                    # Refresh guns if needed
                    if src['type'] == 'gun': self.player.weapon_list[src['gun_idx']]._refresh()
                    if dst['type'] == 'gun': self.player.weapon_list[dst['gun_idx']]._refresh()
                    
                    self.selected_slot_info = None

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

            name_surf = self.font.render(name, True, (255, 255, 255))
            wrapped_info = get_wrapped_lines(info, self.HUD_font, max_w - 2 * padding)
            info_surfs = [self.HUD_font.render(line, True, (200, 200, 200)) for line in wrapped_info]
            
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
            if tip_x + total_w > self.screen_width:
                tip_x = m_x - total_w - 5
            if tip_y + total_h > self.screen_height:
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
                
            self.screen.blit(tip_surf, (tip_x, tip_y))

    # self.DrawLayer2() 
    # self.DrawLayer3() 
    # self.DrawLayer4() 

