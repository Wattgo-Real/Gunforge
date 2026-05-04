
import pygame
from collections import deque

from Asset.GameSetting import BULLET_CONFIG, ATTRIBUTE_MODIFIER_CONFIG

class Gun():
    def __init__(self, basic_info : dict):
        '''
        Basic info of the gun
        '''
        self.basic_cooldown = basic_info["cooldown"]        # Time between shots
        self.basic_reload = basic_info["reload"]  # Time to reload
        self.basic_scatter_angel = basic_info["scatter_angel"]  # Degree of bullet spread
        self.basic_capacity = basic_info["capacity"]  # The maximum number of bullets the gun can hold
        self.card_max_slots = 11     # How many cards can this weapon hold?
        self.card_list = [None] * self.card_max_slots # List of cards attached to the gun
        if basic_info.get("card_list"):
            for i, card in enumerate(basic_info["card_list"]):
                if i < self.card_max_slots:
                    self.card_list[i] = card
        self._refresh()

        # Bullet's default attributes
        self.bullet_lifetime = 1.5  # How long the bullet will stay alive

        self.capacity_left = self.capacity

        self.bullets = pygame.sprite.Group()
        self.cooldown_timer = 0     # Timer for bullet cooldown
        self.reload_timer = 0       # Timer for reload
    
    def _refresh(self):
        self.cooldown = self.basic_cooldown
        self.reload= self.basic_reload
        self.scatter_angel = self.basic_scatter_angel
        self.capacity = self.basic_capacity
        for card in self.card_list:
            if card:
                card.run(self)

    def edit_card(self, new_card, slot : int):
        if slot < len(self.card_list):
            self.card_list[slot] = new_card
            self._refresh()
            return True
        else:
            return False
        
    def fire(self, direction : pygame.Vector2, pos2D : pygame.Vector2): 
        cart_to_bullet = []
        bullet_type = -1
        for card in self.card_list:
            if card is None: continue
            if card.type == 0:  # bullet
                bullet_type = card.bullet_type
                break
            if card.type == 1:  # attribute_modifier
                cart_to_bullet.append(card)

        if bullet_type == -1:
            return False

        if self.cooldown_timer == 0 and self.reload_timer == 0: 
            if self.capacity_left == 0:
                self.capacity_left = self.capacity
            if self.capacity_left <= 0:
                self.capacity_left = 0
                return False

            new_bullet = Bullet(cart_to_bullet, bullet_type, self.bullet_lifetime, pos2D, direction)
            self.bullets.add(new_bullet)
            self.cooldown_timer = self.cooldown

            # Reduce ammo in clip
            self.capacity_left -= 1
            if self.capacity_left == 0:
                self.reload_timer = self.reload
            
            return True
        else:
            return False

    def update(self, delta_time):
        self.cooldown_timer = max(0, self.cooldown_timer - delta_time)
        self.reload_timer = max(0, self.reload_timer - delta_time)

        for bullet in self.bullets:
            bullet.update(delta_time)

        
class Card(pygame.sprite.Sprite):
    def __init__(self, type : int, bullet_type : int = -1, attribute_modifier_type : int = -1):
        '''
        type: 
            0, bullet
            1, attribute_modifier
            2, effect_modifier
        '''
        self.type = type
        self.bullet_type = bullet_type
        self.attribute_modifier_type = attribute_modifier_type

    def run(self, target : Gun):
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
            
    
    def draw(self, surface : pygame.Surface, rect : pygame.Rect):
        if self.type == 0:
            draw_info = BULLET_CONFIG[self.bullet_type][2]
        elif self.type == 1:
            draw_info = ATTRIBUTE_MODIFIER_CONFIG[self.attribute_modifier_type][2]
        start_w = rect.left
        start_h = rect.top
        rect_w = rect.width
        rect_h = rect.height
        for key, value in draw_info.items():
            if key == "circle":
                for circle in value:
                    pos = pygame.math.Vector2(start_w + rect_w * circle["pos_x"], start_h + rect_h * circle["pos_x"])
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
                info += f"\nDamage: {BULLET_CONFIG[self.bullet_type][1].get('damage', 0)}"
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
            return "Effect Modifier", "Special effect card"

        return "Unknown Card", ""

class Bullet(pygame.sprite.Sprite):
    def __init__(self, card_list : list,
                bullet_type : int,
                lifetime : float,
                pos2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                vel2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                acc2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                basic_info : dict = {}):
        '''
        bullet_type:
            0, Normal Bullet
            1, Light Bullet
            2, Heavy Bullet
            3, Grenades 
            4, Laser

        params:
            card_list (list) : List of cards that can be attached to this bullet
            lifetime (float) : How long the bullet will stay alive
            bullet_type (str) : The type of bullet
            pos2D (pygame.Vector2) : The position of the bullet in 2D space
            vel2D (pygame.Vector2) : The velocity of the bullet in 2D space
            acc2D (pygame.Vector2) : The acceleration of the bullet in 2D space
        '''
        super().__init__()
        
        self.card_list = card_list  # List of cards attached to the bullet
        self.lifetime = lifetime    # How long the bullet will stay alive
        self.timer = 0              # Timer for bullet lifetime
        self.bullet_type = bullet_type  # The type of bullet
        
        self.pos2D = pos2D        # The position of the bullet in 2D space
        self.vel2D = vel2D        # The velocity of the bullet in 2D space
        self.acc2D = acc2D        # The acceleration of the bullet in 2D space

        self.init_bullet()

    def init_bullet(self):
        self.damage = BULLET_CONFIG[self.bullet_type][1].get("damage", 0)
        self.speed = BULLET_CONFIG[self.bullet_type][1].get("speed", 0)
        self.lifetime = BULLET_CONFIG[self.bullet_type][1].get("lifetime", self.lifetime)
            
        if self.vel2D.length() != 0:
            self.vel2D = self.vel2D.normalize() * self.speed * 30
        pass
        
    def update(self, delta_time):
        old_vel = pygame.Vector2(self.vel2D)
        self.vel2D = self.vel2D + self.acc2D * delta_time
        self.pos2D = self.pos2D + (old_vel + self.vel2D) * 0.5 * delta_time

        self.timer += delta_time
        if self.timer >= self.lifetime:
            self.kill()

    def triger_hit(self):
        # Handle impact effects here in the future
        self.kill()

    def triger_time(self, ):
        pass

    def triger_lifetime(self, ):
        pass

'''
- 這些 modifier 都會直接附加給 Gun 上，與 bullet 無關
- 基本屬性 ->
	- 散射角 -20 -10 -5 +5 +10 +20
	- 發射間隔冷卻 -0.1 -0.2 -0.4
	- 換彈時間 -0.5 -1 -2
	- 子彈容量 +5 +10 +20
'''
class AttributeModifier():
    def __init__(self, type, value : int):
        '''
        type: 
            0, add_scatter_angel
            1, sub_scatter_angel
            2, add_reload
            3, sub_reload
            4, add_cooldown
            5, sub_cooldown
            6, add_capacity
            7, sub_capacity
            
        value: degree of modification
            2 ** value

        params:
            type (str) : The type of attribute to modify
            value (int) : The degree of modification, 
        '''
        self.type = type
        self.value = value

class EffectModifier():
    def __init__(self, type):
        pass
    pass

