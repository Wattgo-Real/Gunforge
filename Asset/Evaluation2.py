import pygame

def test_screen_eval2(game, events):
    # A simple empty shell for Evaluation 2
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game.test_screen = 4  # Return to Evaluation menu
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cx = game.screen_width // 2
            back_btn = pygame.Rect(cx - 150, 500, 300, 70)
            if back_btn.collidepoint(event.pos):
                game.test_screen = 4

    game.screen.fill((30, 20, 20))
    title_font = pygame.font.SysFont(["consolas", "monaco", "monospace"], 64, bold=True)
    title_surf = title_font.render("Evaluation 2 (Shell)", True, (255, 120, 120))
    game.screen.blit(title_surf, ((game.screen_width - title_surf.get_width()) // 2, 200))

    info_surf = game.font.render("Press ESC or click Back to return to menu.", True, (200, 200, 200))
    game.screen.blit(info_surf, ((game.screen_width - info_surf.get_width()) // 2, 350))

    cx = game.screen_width // 2
    back_btn = pygame.Rect(cx - 150, 500, 300, 70)
    import Asset.Function as GF
    GF.draw_button(game.screen, back_btn, "Back", font=game.font)
