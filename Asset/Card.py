
import pygame

from Asset.GameSetting import BULLET_CONFIG, ATTRIBUTE_MODIFIER_CONFIG, PROJECTILE_MODIFIER_CONFIG, TRIGGER_MODIFIER_CONFIG, MULTIBULLET_MODIFIER_CONFIG
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Asset.Weapons import Bullet
    from Asset.Player import Gun

class Card(pygame.sprite.Sprite):
    def __init__(self, type : int, inter_type : int):
        '''
        type: 
            0, bullet
            1, attribute_modifier
            2, effect_modifier
        '''
        self.type = type
        self.inter_type = inter_type
        

    def run_on_gun(self, target : "Gun"):
        if self.type == 0:  # bullet
            info = BULLET_CONFIG[self.inter_type][1]
        elif self.type == 1:    # attribute_modifier
            info = ATTRIBUTE_MODIFIER_CONFIG[self.inter_type][1]
        elif self.type == 2:    # effect_modifier
            info = PROJECTILE_MODIFIER_CONFIG[self.inter_type][1]
        elif self.type == 3:    # trigger
            info = TRIGGER_MODIFIER_CONFIG[self.inter_type][1]
        elif self.type == 4:    # multibullet
            info = MULTIBULLET_MODIFIER_CONFIG[self.inter_type][1]

        target.cooldown += info.get("cooldown_modifier", 0) 
        target.reload += info.get("reload_modifier", 0) 
        target.scatter_angel += info.get("scatter_angel_modifier", 0) 
        target.capacity += info.get("capacity_modifier", 0) 


    def run_on_bullet(self, target : "Bullet"):
        if self.type == 1:    # attribute_modifier
            info = ATTRIBUTE_MODIFIER_CONFIG[self.inter_type][1]
            if self.inter_type >= 100:
                if self.inter_type == 100:
                    target.phy_damage += target.speed / 2
                elif self.inter_type == 101:
                    target.speed += target.phy_damage / 2
            elif self.inter_type >= 50 and self.inter_type < 100:
                target.speed += info.get("bullet_speed_modifier", 0) 
                target.phy_damage += info.get("physical_damage_modifier", 0)
                target.exp_damage += info.get("explosion_damage_modifier", 0)
                target.bur_damage += info.get("burn_damage_modifier", 0)
                target.explosion_radius += info.get("explosion_radius_modifier", 0)
                
        elif self.type == 3: # trigger_modifier
            target.trigger_type = self.inter_type
            if self.inter_type == 2:
                target.trigger_time = 0.1
            elif self.inter_type == 3:
                target.trigger_time = 0.2
            elif self.inter_type == 4:
                target.trigger_time = 0.5
            elif self.inter_type == 5:
                target.trigger_time = 1.0
            
    def draw(self, surface : pygame.Surface, rect : pygame.Rect):
        if self.type == 0:
            draw_info = BULLET_CONFIG[self.inter_type][2]
        elif self.type == 1:
            draw_info = ATTRIBUTE_MODIFIER_CONFIG[self.inter_type][2]
        elif self.type == 2:
            draw_info = PROJECTILE_MODIFIER_CONFIG[self.inter_type][2]
        elif self.type == 3:
            draw_info = TRIGGER_MODIFIER_CONFIG[self.inter_type][2]
        elif self.type == 4:
            draw_info = MULTIBULLET_MODIFIER_CONFIG[self.inter_type][2]

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
            if self.inter_type in BULLET_CONFIG:
                name = BULLET_CONFIG[self.inter_type][0]
                info = BULLET_CONFIG[self.inter_type][1].get("info", "")
                CONFIG = BULLET_CONFIG[self.inter_type][1]
                
        elif self.type == 1: # attribute_modifier
            if self.inter_type in ATTRIBUTE_MODIFIER_CONFIG:
                name = ATTRIBUTE_MODIFIER_CONFIG[self.inter_type][0]
                info = ATTRIBUTE_MODIFIER_CONFIG[self.inter_type][1].get("info", "")
                CONFIG = ATTRIBUTE_MODIFIER_CONFIG[self.inter_type][1]

        elif self.type == 2: # effect_modifier
           if self.inter_type in PROJECTILE_MODIFIER_CONFIG:
               name = PROJECTILE_MODIFIER_CONFIG[self.inter_type][0]
               info = PROJECTILE_MODIFIER_CONFIG[self.inter_type][1].get("info", "")
               CONFIG = PROJECTILE_MODIFIER_CONFIG[self.inter_type][1]

        elif self.type == 3: # trigger_modifier
           if self.inter_type in TRIGGER_MODIFIER_CONFIG:
               name = TRIGGER_MODIFIER_CONFIG[self.inter_type][0]
               info = TRIGGER_MODIFIER_CONFIG[self.inter_type][1].get("info", "")
               CONFIG = TRIGGER_MODIFIER_CONFIG[self.inter_type][1]

        elif self.type == 4: # multibullet
           if self.inter_type in MULTIBULLET_MODIFIER_CONFIG:
               name = MULTIBULLET_MODIFIER_CONFIG[self.inter_type][0]
               info = MULTIBULLET_MODIFIER_CONFIG[self.inter_type][1].get("info", "")
               CONFIG = MULTIBULLET_MODIFIER_CONFIG[self.inter_type][1] 

        if info != "":
            if len(CONFIG) > 1:
                info += "\n--------------------\n"
            if "default_trigger" in CONFIG:
                info += f"\nDefault Trigger: {CONFIG.get('default_trigger', 0)}"
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
