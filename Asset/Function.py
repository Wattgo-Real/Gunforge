import pygame


def draw_button(
    screen, rect, text, font, color=(100, 100, 255), text_color=(255, 255, 255)
):
    pygame.draw.rect(screen, color, rect)
    label = font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))
