import pygame


def draw_button(
    screen, rect, text, font, color=(100, 100, 255), text_color=(255, 255, 255)
):
    pygame.draw.rect(screen, (100, 100, 255), rect)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))
