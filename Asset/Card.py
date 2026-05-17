
import pygame

from Asset.GameSetting import BULLET_CONFIG, ATTRIBUTE_MODIFIER_CONFIG, EFFECT_MODIFIER_CONFIG, COLOR_CONFIG
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Asset.Weapons import Bullet
    from Asset.Player import Gun

class Card(pygame.sprite.Sprite):
    def __init__(self, type : int, bullet_type : int = -1, attribute_modifier_type : int = -1, effect_modifier_type : int = -1):
        '''
        type: 
            0, bullet
            1, attribute_modifier
            2, effect_modifier
        '''
        self.type = type
        self.bullet_type = bullet_type
        self.attribute_modifier_type = attribute_modifier_type

        self.effect_modifier_type = effect_modifier_type

    def run_on_gun(self, target : "Gun"):
        if self.type == 0:  # bullet
            info = BULLET_CONFIG[self.bullet_type][1]
        elif self.type == 1:    # attribute_modifier
            info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]
        elif self.type == 2:    # effect_modifier
            info = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][1]

        target.cooldown += info.get("cooldown_modifier", 0) 
        target.reload += info.get("reload_modifier", 0) 
        target.scatter_angel += info.get("scatter_angel_modifier", 0) 
        target.capacity += info.get("capacity_modifier", 0) 


    def run_on_bullet(self, target : "Bullet"):
        if self.type == 1:    # attribute_modifier
            info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]
            if self.attribute_modifier_type >= 0 and self.attribute_modifier_type < 50:
                if self.attribute_modifier_type == 0:
                    target.phy_damage += target.speed / 2
                if self.attribute_modifier_type == 1:
                    target.speed += target.phy_damage / 2
            elif self.attribute_modifier_type >= 50 and self.attribute_modifier_type < 100:
                target.speed += info.get("bullet_speed_modifier", 0) 

            
    def draw(self, surface : pygame.Surface, rect : pygame.Rect):
        if self.type == 0:
            draw_info = BULLET_CONFIG[self.bullet_type][2]
        elif self.type == 1:
            draw_info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][2]
        elif self.type == 2:
            draw_info = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][2]
            
        start_w = rect.left
        start_h = rect.top
        rect_w = rect.width
        rect_h = rect.height
        if rect_w != rect_h:
            min_size = min(rect_w, rect_h)
            start_w += (rect_w - min_size) // 2
            start_h += (rect_h - min_size) // 2
            rect_w = min_size
            rect_h = min_size
        
        for key, value in draw_info.items():
            if key == "circle":
                for circle in value:
                    pos = pygame.math.Vector2(start_w + rect_w * circle["pos_x"], start_h + rect_h * circle["pos_y"])
                    color = circle["color"]
                    size = int(rect_w / 2 * circle["size"])
                    pygame.draw.circle(surface, color, pos, size)
            elif key == "line":
                for line in value:
                    start_pos = pygame.math.Vector2(start_w + rect_w * line["start_x"], start_h + rect_h * line["start_y"])
                    end_pos = pygame.math.Vector2(start_w + rect_w * line["end_x"], start_h + rect_h * line["end_y"])
                    color = line["color"]
                    width = int(rect_w * line["width"])
                    pygame.draw.line(surface, color, start_pos, end_pos, width)

    def get_info(self):
        name = ""
        info = ""
        if self.type == 0: # bullet
            if self.bullet_type in BULLET_CONFIG:
                name = BULLET_CONFIG[self.bullet_type][0]
                info = BULLET_CONFIG[self.bullet_type][1].get("info", "")
                CONFIG = BULLET_CONFIG[self.bullet_type][1]
        elif self.type == 1: # attribute_modifier
            if self.attribute_modifier_type in ATTRIBUTE_MODIFIER_CONFIG:
                name = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][0]
                info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1].get("info", "")
                CONFIG = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]

        elif self.type == 2: # effect_modifier
           if self.effect_modifier_type in EFFECT_MODIFIER_CONFIG:
               name = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][0]
               info = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][1].get("info", "")
               CONFIG = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][1]
               
        if "default_trigger" in CONFIG:
            info += f"\nDefault Trigger: {CONFIG.get('default_trigger', 0)}"
            
        if info != "":
            if len(CONFIG) > 1:
                info += "\n--------------------\n"
            if "speed" in CONFIG:
                info += f"\nSpeed: {CONFIG.get('speed', 0)}"
            if "physical_damage" in CONFIG:
                info += f"\nPhysical Damage: {CONFIG.get('physical_damage', 0)}"
            if "explosion_damage" in CONFIG:
                info += f"\nExplosion Damage: {CONFIG.get('explosion_damage', 0)}"
            if "explosion_radius" in CONFIG:
                info += f"\nExplosion Radius: {CONFIG.get('explosion_radius', 0)}"
            if "burn_damage" in CONFIG:
                info += f"\nBurn Damage: {CONFIG.get('burn_damage', 0)}"
            if "radius" in CONFIG:
                info += f"\nExplosion Radius: {CONFIG.get('radius', 0)}"

            if "cooldown_modifier" in CONFIG:
                info += f"\nCooldown Modifier: {CONFIG.get('cooldown_modifier', 0)}"
            if "reload_modifier" in CONFIG:
                info += f"\nReload Modifier: {CONFIG.get('reload_modifier', 0)}"
            if "capacity_modifier" in CONFIG:
                info += f"\nCapacity Modifier: {CONFIG.get('capacity_modifier', 0)}"
            if "scatter_angel_modifier" in CONFIG:
                info += f"\nScatter Modifier: {CONFIG.get('scatter_angel_modifier', 0)}"

            if "bullet_speed_modifier" in CONFIG:
                info += f"\nSpeed Modifier: {CONFIG.get('bullet_speed_modifier', 0)}"

            return name, info

        return "Unknown Card", ""
