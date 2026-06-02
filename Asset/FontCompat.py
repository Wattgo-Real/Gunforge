"""Compatibility wrapper for pygame font rendering.

pygame 2.6.1 on Python 3.14 can fail to import pygame.font because
pygame.font and pygame.sysfont import each other during module loading.
This module provides the small pygame.font API surface used by the game.
"""

from __future__ import annotations

import pygame._freetype as _freetype


class Font:
    def __init__(self, file=None, size=24, bold=False, italic=False):
        _freetype.init()
        self._font = _freetype.Font(file, max(1, int(size)))
        self._font.antialiased = True
        self._font.origin = True
        self._font.pad = True
        self._font.strong = bool(bold)
        self._font.oblique = bool(italic)

    def render(self, text, antialias, color, background=None):
        old_antialias = self._font.antialiased
        self._font.antialiased = bool(antialias)
        try:
            surface, _ = self._font.render("" if text is None else str(text), color, background)
            return surface
        finally:
            self._font.antialiased = old_antialias

    def size(self, text):
        rect = self._font.get_rect("" if text is None else str(text))
        return rect.width, rect.height

    def get_linesize(self):
        return self._font.get_sized_height()

    def get_height(self):
        return self.get_linesize()

    def set_bold(self, value):
        self._font.strong = bool(value)

    def get_bold(self):
        return self._font.strong

    def set_italic(self, value):
        self._font.oblique = bool(value)

    def get_italic(self):
        return self._font.oblique


class _FontModule:
    Font = Font

    def init(self):
        _freetype.init()

    def quit(self):
        _freetype.quit()

    def get_init(self):
        return _freetype.get_init()

    def get_default_font(self):
        return _freetype.get_default_font()

    def SysFont(self, name, size, bold=False, italic=False):
        return Font(None, size, bold=bold, italic=italic)

    def match_font(self, name, bold=False, italic=False):
        return None

    def get_fonts(self):
        return []


def install_pygame_font_compat(pygame_module):
    pygame_module.font = _FontModule()
    return pygame_module.font
