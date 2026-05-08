
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
            target.cooldown += info.get("cooldown_modifier", 0) 
            target.reload += info.get("reload_modifier", 0) 
            target.scatter_angel += info.get("scatter_angel_modifier", 0) 
            target.capacity += info.get("capacity_modifier", 0) 
            
            
        elif self.type == 1:    # attribute_modifier
            info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]
            target.cooldown += info.get("cooldown_modifier", 0) 
            target.reload += info.get("reload_modifier", 0) 
            target.scatter_angel += info.get("scatter_angel_modifier", 0) 
            target.capacity += info.get("capacity_modifier", 0) 

        elif self.type == 2:    # effect_modifier
            pass

    def run_on_bullet(self, target : "Bullet"):
        if self.type == 2:    # effect_modifier
            info = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][1]
            if self.effect_modifier_type >= 0 and self.effect_modifier_type < 50:
                pass
            elif self.effect_modifier_type >= 50 and self.effect_modifier_type < 100:
                target.speed += info.get("bullet_speed_modifier", 0) 
            elif self.effect_modifier_type >= 100 and self.effect_modifier_type < 150:
                pass
            pass
            
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
        if self.type == 0: # bullet
            if self.bullet_type in BULLET_CONFIG:
                name = BULLET_CONFIG[self.bullet_type][0]
                info = BULLET_CONFIG[self.bullet_type][1].get("info", "")
                info += f"\nSpeed: {BULLET_CONFIG[self.bullet_type][1].get('speed', 0)}"
                if "physical_damage" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nPhysical Damage: {BULLET_CONFIG[self.bullet_type][1].get('physical_damage', 0)}"
                if "explosion_damage" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nExplosion Damage: {BULLET_CONFIG[self.bullet_type][1].get('explosion_damage', 0)}"
                if "burn_damage" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nBurn Damage: {BULLET_CONFIG[self.bullet_type][1].get('burn_damage', 0)}"
                if "radius" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nExplosion Radius: {BULLET_CONFIG[self.bullet_type][1].get('radius', 0)}"
                if "cooldown_modifier" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nCooldown Modifier: {BULLET_CONFIG[self.bullet_type][1].get('cooldown_modifier', 0)}"
                if "reload_modifier" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nReload Modifier: {BULLET_CONFIG[self.bullet_type][1].get('reload_modifier', 0)}"
                if "capacity_modifier" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nCapacity Modifier: {BULLET_CONFIG[self.bullet_type][1].get('capacity_modifier', 0)}"
                if "scatter_angel_modifier" in BULLET_CONFIG[self.bullet_type][1]:
                    info += f"\nScatter Modifier: {BULLET_CONFIG[self.bullet_type][1].get('scatter_angel_modifier', 0)}"
                
                return name, info
        elif self.type == 1: # attribute_modifier
            if self.attribute_modifier_type in ATTRIBUTE_MODIFIER_CONFIG:
                name = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][0]
                info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1].get("info", "")
                if "cooldown_modifier" in ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]:
                    info += f"\nCooldown Modifier: {ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1].get('cooldown_modifier', 0)}"
                if "reload_modifier" in ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]:
                    info += f"\nReload Modifier: {ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1].get('reload_modifier', 0)}"
                if "capacity_modifier" in ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]:
                    info += f"\nCapacity Modifier: {ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1].get('capacity_modifier', 0)}"
                if "scatter_angel_modifier" in ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1]:
                    info += f"\nScatter Modifier: {ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][1].get('scatter_angel_modifier', 0)}"
                return name, info
                
        elif self.type == 2: # effect_modifier
           if self.effect_modifier_type in EFFECT_MODIFIER_CONFIG:
               name = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][0]
               info = EFFECT_MODIFIER_CONFIG[self.effect_modifier_type][1].get("info", "")
               return name, info

        return "Unknown Card", ""
