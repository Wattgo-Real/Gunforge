from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from Start import Game

import Asset.Function as GF
from Asset.Card import Card
from Asset.ShopConfig import (
    CARD_TYPE_LABELS,
    SHOP_CARD_CATALOG,
    STAT_UPGRADES,
    card_key_to_tuple,
    ensure_shop_state,
    upgrade_cost,
)
from Asset.TestScreen1 import reset_screen1


def _buy_upgrade(game: "Game", key, config):
    ensure_shop_state(game)
    level = game.shop_upgrades[key]
    cost = upgrade_cost(config, level)
    if cost is None:
        return
    if game.total_points < cost:
        game.shop_message = ["Not enough points", 1.4, (255, 130, 120)]
        return

    game.total_points -= cost
    game.shop_upgrades[key] += 1
    game.shop_message = [f"Purchased {config['label']}", 1.4, (255, 220, 120)]


def _buy_selected_card(game: "Game"):
    ensure_shop_state(game)
    selected_key = getattr(game, "shop_selected_card", None)
    if selected_key is None:
        game.shop_message = ["Select a card first", 1.4, (255, 130, 120)]
        return
    if selected_key in game.shop_owned_cards:
        game.shop_message = ["Card already owned", 1.4, (255, 220, 120)]
        return

    card_info = next((card for card in SHOP_CARD_CATALOG if card["key"] == selected_key), None)
    if card_info is None:
        return
    if game.total_points < card_info["cost"]:
        game.shop_message = ["Not enough points", 1.4, (255, 130, 120)]
        return

    game.total_points -= card_info["cost"]
    game.shop_owned_cards.add(selected_key)
    card_name, _ = Card(type=card_info["type"], inter_type=card_info["id"]).get_info()
    game.shop_message = [f"Purchased {card_name}", 1.4, (255, 220, 120)]


def _draw_text(surface, font, text, pos, color=(230, 230, 235)):
    surface.blit(font.render(text, True, color), pos)


def _draw_wrapped_text(surface, font, text, rect, color=(210, 215, 225), line_gap=4):
    y = rect.top
    for paragraph in text.splitlines():
        words = paragraph.split()
        if not words:
            y += font.get_linesize() + line_gap
            continue
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if font.size(candidate)[0] <= rect.width:
                line = candidate
            else:
                if line:
                    surface.blit(font.render(line, True, color), (rect.left, y))
                    y += font.get_linesize() + line_gap
                line = word
                if y + font.get_linesize() > rect.bottom:
                    return
        if line and y + font.get_linesize() <= rect.bottom:
            surface.blit(font.render(line, True, color), (rect.left, y))
            y += font.get_linesize() + line_gap
        if y + font.get_linesize() > rect.bottom:
            return


def _draw_upgrade_row(game: "Game", rect, key, config, mouse_pos):
    level = game.shop_upgrades[key]
    max_level = config["max_level"]
    cost = upgrade_cost(config, level)
    can_buy = cost is not None and game.total_points >= cost
    hovered = rect.collidepoint(mouse_pos)
    fill = (34, 38, 48) if not hovered else (44, 50, 62)
    pygame.draw.rect(game.screen, fill, rect, border_radius=6)
    pygame.draw.rect(game.screen, (82, 88, 108), rect, 1, border_radius=6)

    _draw_text(game.screen, game.font, config["label"], (rect.left + 16, rect.top + 12))
    _draw_text(
        game.screen,
        game.HUD_font,
        f"Lv {level}/{max_level}   {config.get('unit', '')}",
        (rect.left + 16, rect.top + 44),
        (180, 190, 210),
    )

    if cost is None:
        text = "MAX"
        color = (130, 210, 160)
    else:
        text = f"Buy {cost}"
        color = (255, 220, 120) if can_buy else (140, 145, 155)
    label = game.font.render(text, True, color)
    game.screen.blit(label, label.get_rect(center=(rect.right - 74, rect.centery)))


def _layout(game: "Game"):
    margin = 48
    gap = 28
    top = 160
    bottom = 118
    stat_w = min(340, max(260, int(game.screen_width * 0.33)))
    card_w = game.screen_width - margin * 2 - gap - stat_w
    left_x = margin
    right_x = margin + stat_w + gap

    stat_rects = []
    y = top + 46
    for key, config in STAT_UPGRADES.items():
        stat_rects.append((key, config, pygame.Rect(left_x, y, stat_w, 76)))
        y += 90

    detail_h = 126
    grid_top = top + 46
    grid_h = max(120, game.screen_height - grid_top - bottom - detail_h - 14)
    grid_rect = pygame.Rect(right_x, grid_top, card_w, grid_h)
    detail_rect = pygame.Rect(right_x, grid_rect.bottom + 14, card_w, detail_h)

    return stat_rects, grid_rect, detail_rect


def _card_grid_rects(grid_rect, scroll):
    icon_size = 54
    gap = 10
    cols = max(1, grid_rect.width // (icon_size + gap))
    content_w = cols * icon_size + (cols - 1) * gap
    start_x = grid_rect.left + max(0, (grid_rect.width - content_w) // 2)
    rects = []
    for i, card_info in enumerate(SHOP_CARD_CATALOG):
        col = i % cols
        row = i // cols
        x = start_x + col * (icon_size + gap)
        y = grid_rect.top + row * (icon_size + gap) - scroll
        rects.append((card_info, pygame.Rect(x, y, icon_size, icon_size)))
    rows = (len(SHOP_CARD_CATALOG) + cols - 1) // cols
    content_h = rows * icon_size + max(0, rows - 1) * gap
    return rects, content_h


def _clamp_card_scroll(game, grid_rect):
    scroll = getattr(game, "shop_card_scroll", 0)
    _, content_h = _card_grid_rects(grid_rect, 0)
    max_scroll = max(0, content_h - grid_rect.height)
    game.shop_card_scroll = max(0, min(scroll, max_scroll))


def _draw_card_grid(game: "Game", grid_rect, mouse_pos):
    pygame.draw.rect(game.screen, (24, 27, 36), grid_rect, border_radius=6)
    pygame.draw.rect(game.screen, (82, 88, 108), grid_rect, 1, border_radius=6)
    old_clip = game.screen.get_clip()
    game.screen.set_clip(grid_rect)
    card_rects, content_h = _card_grid_rects(grid_rect, game.shop_card_scroll)
    selected = getattr(game, "shop_selected_card", None)
    for card_info, rect in card_rects:
        if rect.bottom < grid_rect.top or rect.top > grid_rect.bottom:
            continue
        owned = card_info["key"] in game.shop_owned_cards
        hovered = rect.collidepoint(mouse_pos)
        fill = (33, 36, 46) if not hovered else (48, 54, 68)
        pygame.draw.rect(game.screen, fill, rect, border_radius=5)
        Card(type=card_info["type"], inter_type=card_info["id"]).draw(game.screen, rect.inflate(-6, -6))
        if card_info["key"] == selected:
            border = (120, 190, 255)
            width = 3
        elif owned:
            border = (255, 220, 120)
            width = 2
        else:
            border = (92, 98, 116)
            width = 1
        pygame.draw.rect(game.screen, border, rect, width, border_radius=5)
        if not owned:
            cost = game.HUD_font.render(str(card_info["cost"]), True, (255, 220, 120))
            game.screen.blit(cost, (rect.right - cost.get_width() - 4, rect.bottom - cost.get_height() - 2))
    game.screen.set_clip(old_clip)

    if content_h > grid_rect.height:
        bar_h = max(24, int(grid_rect.height * grid_rect.height / content_h))
        max_scroll = content_h - grid_rect.height
        bar_y = grid_rect.top + int((grid_rect.height - bar_h) * (game.shop_card_scroll / max_scroll))
        scroll_bar = pygame.Rect(grid_rect.right - 7, bar_y, 4, bar_h)
        pygame.draw.rect(game.screen, (120, 130, 150), scroll_bar, border_radius=2)

    return card_rects


def _draw_selected_card(game: "Game", detail_rect):
    pygame.draw.rect(game.screen, (28, 31, 40), detail_rect, border_radius=6)
    pygame.draw.rect(game.screen, (82, 88, 108), detail_rect, 1, border_radius=6)
    selected = getattr(game, "shop_selected_card", None)
    if selected is None and SHOP_CARD_CATALOG:
        selected = SHOP_CARD_CATALOG[0]["key"]
        game.shop_selected_card = selected
    card_info = next((card for card in SHOP_CARD_CATALOG if card["key"] == selected), None)
    if card_info is None:
        return None

    card = Card(type=card_info["type"], inter_type=card_info["id"])
    name, info = card.get_info()
    icon_rect = pygame.Rect(detail_rect.left + 12, detail_rect.top + 18, 76, 76)
    pygame.draw.rect(game.screen, (18, 20, 26), icon_rect, border_radius=5)
    card.draw(game.screen, icon_rect)
    pygame.draw.rect(game.screen, (120, 190, 255), icon_rect, 2, border_radius=5)

    owned = card_info["key"] in game.shop_owned_cards
    label_color = (255, 220, 120) if owned else (235, 240, 250)
    _draw_text(game.screen, game.font, name, (detail_rect.left + 104, detail_rect.top + 12), label_color)
    meta = f"{CARD_TYPE_LABELS.get(card_info['type'], 'Card')} | {card_info['tier']} | Cost {card_info['cost']}"
    if owned:
        meta += " | Owned"
    _draw_text(game.screen, game.HUD_font, meta, (detail_rect.left + 104, detail_rect.top + 40), (170, 185, 205))
    _draw_wrapped_text(
        game.screen,
        game.HUD_font,
        info or "No description.",
        pygame.Rect(detail_rect.left + 104, detail_rect.top + 62, detail_rect.width - 244, detail_rect.height - 70),
        (205, 212, 224),
    )

    buy_btn = pygame.Rect(detail_rect.right - 126, detail_rect.bottom - 52, 108, 36)
    if owned:
        GF.draw_button(game.screen, buy_btn, "Owned", font=game.HUD_font, color=(70, 90, 75))
    else:
        can_buy = game.total_points >= card_info["cost"]
        color = (100, 100, 255) if can_buy else (70, 72, 84)
        GF.draw_button(game.screen, buy_btn, "Buy", font=game.HUD_font, color=color)
    return buy_btn


def test_screen_shop(game: "Game", events):
    ensure_shop_state(game)
    if not hasattr(game, "shop_message"):
        game.shop_message = None
    if not hasattr(game, "shop_card_scroll"):
        game.shop_card_scroll = 0

    mouse_pos = pygame.mouse.get_pos()
    stat_rects, grid_rect, detail_rect = _layout(game)
    _clamp_card_scroll(game, grid_rect)
    enter_btn = pygame.Rect(0, 0, 260, 58)
    back_btn = pygame.Rect(0, 0, 180, 58)
    enter_btn.center = (game.screen_width // 2 + 115, game.screen_height - 64)
    back_btn.center = (game.screen_width // 2 - 140, game.screen_height - 64)
    buy_card_btn = None

    for event in events:
        if event.type == pygame.MOUSEWHEEL:
            if grid_rect.collidepoint(mouse_pos):
                game.shop_card_scroll -= event.y * 72
                _clamp_card_scroll(game, grid_rect)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if enter_btn.collidepoint(event.pos):
                reset_screen1(game)
                game.test_screen = 1
                return
            if back_btn.collidepoint(event.pos):
                game.test_screen = 0
                return
            buy_card_btn = _selected_buy_button_rect(detail_rect)
            if buy_card_btn.collidepoint(event.pos):
                _buy_selected_card(game)
                continue
            for key, config, rect in stat_rects:
                if rect.collidepoint(event.pos):
                    _buy_upgrade(game, key, config)
                    break
            else:
                for card_info, rect in _card_grid_rects(grid_rect, game.shop_card_scroll)[0]:
                    if grid_rect.colliderect(rect) and rect.collidepoint(event.pos):
                        game.shop_selected_card = card_info["key"]
                        break

    game.screen.fill((16, 18, 26))
    title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 58, bold=True)
    title = title_font.render("SHOP", True, (255, 220, 120))
    game.screen.blit(title, title.get_rect(center=(game.screen_width // 2, 64)))
    points = game.font.render(f"Available points: {game.total_points}", True, (220, 230, 245))
    game.screen.blit(points, points.get_rect(center=(game.screen_width // 2, 112)))

    _draw_text(game.screen, game.font, "Player Stats", (stat_rects[0][2].left, 160), (160, 210, 255))
    _draw_text(game.screen, game.font, "Cards", (grid_rect.left, 160), (160, 210, 255))

    for key, config, rect in stat_rects:
        _draw_upgrade_row(game, rect, key, config, mouse_pos)
    card_rects = _draw_card_grid(game, grid_rect, mouse_pos)
    buy_card_btn = _draw_selected_card(game, detail_rect)

    hovered_card = None
    if grid_rect.collidepoint(mouse_pos):
        for card_info, rect in card_rects:
            if rect.bottom < grid_rect.top or rect.top > grid_rect.bottom:
                continue
            if rect.collidepoint(mouse_pos):
                hovered_card = Card(type=card_info["type"], inter_type=card_info["id"])
                break

    if game.shop_message:
        text, timer, color = game.shop_message
        timer -= game.delta_time
        if timer <= 0:
            game.shop_message = None
        else:
            game.shop_message[1] = timer
            surf = game.font.render(text, True, color)
            game.screen.blit(surf, surf.get_rect(center=(game.screen_width // 2, game.screen_height - 118)))

    GF.draw_button(game.screen, back_btn, "Back", font=game.font, color=(75, 82, 105))
    GF.draw_button(game.screen, enter_btn, "Enter Game", font=game.font, color=(100, 100, 255))

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
        tip_x = mouse_pos[0] + 15
        tip_y = mouse_pos[1] + 15

        # Adjust if off-screen
        if tip_x + total_w > game.screen_width:
            tip_x = mouse_pos[0] - total_w - 5
        if tip_y + total_h > game.screen_height:
            tip_y = mouse_pos[1] - total_h - 5

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


def _selected_buy_button_rect(detail_rect):
    return pygame.Rect(detail_rect.right - 126, detail_rect.bottom - 52, 108, 36)
