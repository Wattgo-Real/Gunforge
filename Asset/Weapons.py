

import pygame
from collections import deque
import random
import copy

from Asset.GameSetting import BULLET_CONFIG, ATTRIBUTE_MODIFIER_CONFIG, EFFECT_MODIFIER_CONFIG, COLOR_CONFIG, GRID_CONFIG
from Asset.GameSetting import ENTITY_TYPE
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Asset.Card import Card
    #from Asset.Enemies import Enemy
    
import uuid

class Gun():
    def __init__(self, basic_info : dict, bullet_manager):
        '''
        Basic info of the gun
        '''
        self.basic_cooldown = basic_info["cooldown"]        # Time between shots
        self.basic_reload = basic_info["reload"]  # Time to reload
        self.basic_scatter_angel = basic_info["scatter_angel"]  # Degree of bullet spread
        self.basic_capacity = basic_info["capacity"]  # The maximum number of bullets the gun can hold
        self.card_max_slots = basic_info["max_slots"]     # How many cards can this weapon hold?
        self.card_list = [None] * self.card_max_slots # List of cards attached to the gun
        if basic_info.get("card_list"):
            for i, card in enumerate(basic_info["card_list"]):
                if i < self.card_max_slots:
                    self.card_list[i] = card
        self.capacity_left = self.basic_capacity
        self._refresh()

        self.max_effect_count = 3


        self.cooldown_timer = 0     # Timer for bullet cooldown
        self.reload_timer = 0       # Timer for reload

        self.bullet_manager = bullet_manager

    def _refresh(self):
        self.cooldown = self.basic_cooldown
        self.reload= self.basic_reload
        self.scatter_angel = self.basic_scatter_angel
        self.capacity = self.basic_capacity
        for card in self.card_list:
            if card:
                card.run_on_gun(self)

        if self.capacity_left > self.capacity:
            self.capacity_left = self.capacity
        if self.scatter_angel < 0:
            self.scatter_angel = 0
        if self.reload < 0:
            self.reload = 0
        if self.cooldown < 0:
            self.cooldown = 0
        
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
        effect_card_count = 0
        for card in self.card_list:
            if card is None: continue
            if card.type == 0:  # bullet
                bullet_type = card.bullet_type
                continue
            if card.type == 1:  # attribute
                if card.attribute_modifier_type >= 50:
                    cart_to_bullet.append(card)
                continue
            if card.type == 2:  # effect
                if effect_card_count >= self.max_effect_count:
                    continue
                cart_to_bullet.append(card)
                effect_card_count += 1

        if bullet_type == -1:
            return "No bullet card equipped!"

        if self.cooldown_timer == 0 and self.reload_timer == 0: 
            if self.capacity_left == 0:
                self.capacity_left = self.capacity
            if self.capacity_left <= 0:
                self.capacity_left = 0
                return "No bullet in clip!"

            direction = direction.rotate(random.uniform(-self.scatter_angel, self.scatter_angel))
            self.bullet_manager.add_bullet(cart_to_bullet, bullet_type, pos2D, direction)
            self.cooldown_timer = self.cooldown

            # Reduce ammo in clip
            self.capacity_left -= 1
            if self.capacity_left == 0:
                self.reload_timer = self.reload
            return ""
        else:
            if self.reload_timer > 0:
                return "Gun is reloading"
            else:
                return ""

    def update(self, delta_time):
        self.cooldown_timer = max(0, self.cooldown_timer - delta_time)
        self.reload_timer = max(0, self.reload_timer - delta_time)


class BulletManager():
    def __init__(self, spatial_grid_dict):
        self.bullets = pygame.sprite.Group()
        self.spatial_grid_dict = spatial_grid_dict
        self.player = None

    def add_bullet(self, cart_to_bullet, bullet_type, pos2D, direction):
        new_bullet = Bullet(cart_to_bullet, bullet_type, self.player, self.spatial_grid_dict, pos2D, direction)
        self.bullets.add(new_bullet)

    def update(self, delta_time):
        for bullet in self.bullets:
            bullet.update(delta_time)
            if bullet.status == 0:
                self.check_card_status(bullet)
                bullet.status = -1

            if bullet.isKill == True:
                del self.spatial_grid_dict[bullet.grid_pos][bullet.uuid]
                bullet.kill()
    
    def check_card_status(self, bullet):
        for card in bullet.card_list:
            if card.type == 2:
                bullet.isKill = True
                if card.effect_modifier_type < 2:   # Split
                    new_cards = bullet.card_list.copy()
                    new_cards.remove(card)
                    pos2D, vel2D, acc2D = bullet.pos2D, bullet.vel2D, bullet.acc2D
                    hit_enemies = bullet.hit_enemies

                    if card.effect_modifier_type == 0:
                        vel2D_v1 = vel2D.rotate(45)
                        vel2D_v2 = vel2D.rotate(-45)
                    elif card.effect_modifier_type == 1:
                        vel2D_v1 = vel2D.rotate(135)
                        vel2D_v2 = vel2D.rotate(-135)

                    new_bullet = Bullet(new_cards, bullet.bullet_type, self.player, self.spatial_grid_dict, pos2D, vel2D_v1, acc2D, hit_enemies = hit_enemies)
                    new_bullet.multiplier = bullet.multiplier * 0.5
                    self.bullets.add(new_bullet)

                    new_bullet = Bullet(new_cards, bullet.bullet_type, self.player, self.spatial_grid_dict, pos2D, vel2D_v2, acc2D, hit_enemies = hit_enemies)
                    new_bullet.multiplier = bullet.multiplier * 0.5
                    self.bullets.add(new_bullet)

                    break

                elif card.effect_modifier_type == 2:    # Penetrate
                    new_cards = bullet.card_list.copy()
                    new_cards.remove(card)
                    bullet.card_list = new_cards
                    bullet.isKill = False

                    break

                elif card.effect_modifier_type == 3:  # Bounce
                    new_cards = bullet.card_list.copy()
                    new_cards.remove(card)
                    bullet.card_list = new_cards
                    bullet.isKill = False

                    target = getattr(bullet, "last_hit_target", None)
                    if target is not None:
                        if target.entity_type == ENTITY_TYPE["enemy"]:
                            # Bounce off enemy: reverse velocity or push away
                            normal = (bullet.pos2D - target.pos2D)
                            if normal.length_squared() > 0:
                                normal = normal.normalize()
                                dot = bullet.vel2D.dot(normal)
                                bullet.vel2D = bullet.vel2D - 2 * dot * normal
                                bullet.pos2D += normal * (bullet.radius + target.radius + 2)
                        elif target.entity_type == ENTITY_TYPE["obstacle"]:
                            # Bounce off obstacle (rectangle)
                            half = target.size / 2
                            local_pos = bullet.pos2D - target.pos2D

                            overlap_x = half.x - abs(local_pos.x)
                            overlap_y = half.y - abs(local_pos.y)
                            
                            normal = pygame.Vector2(0, 0)
                            if overlap_x < overlap_y:
                                normal.x = 1 if local_pos.x > 0 else -1
                                bullet.pos2D.x = target.pos2D.x + normal.x * (half.x + bullet.radius + 2)
                            else:
                                normal.y = 1 if local_pos.y > 0 else -1
                                bullet.pos2D.y = target.pos2D.y + normal.y * (half.y + bullet.radius + 2)

                            if normal.length_squared() > 0:
                                dot = bullet.vel2D.dot(normal)
                                bullet.vel2D = bullet.vel2D - 2 * dot * normal

                    break
    
                    



class Bullet(pygame.sprite.Sprite):
    def __init__(self, card_list : list["Card"],
                bullet_type : int,
                player,
                spatial_grid_dict : dict,
                pos2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                vel2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                acc2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                basic_info : dict = {},
                hit_enemies : set = set()):
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
        self.uuid = uuid.uuid4()    # unique identifier of the spatial partitioning
        self.entity_type = ENTITY_TYPE["bullet"]
        self.bullet_type = bullet_type  # The type of bullet

        self.pos2D = pos2D        # The position of the bullet in 2D space
        self.vel2D = vel2D        # The velocity of the bullet in 2D space
        self.acc2D = acc2D        # The acceleration of the bullet in 2D space
        self.hit_enemies = hit_enemies.copy()  # Track enemies already hit by this bullet
        self.multiplier = 1


        self.card_list : list[Card] = card_list  # List of cards attached to the bullet
        
        self.lifetime = 2    # How long the bullet will stay alive
        self.timer = 0              # Timer for bullet lifetime
        self.status = -1     # -1 nothing, 0 hit, 1 lifetime, 2 time
        

        self.spatial_grid_dict = spatial_grid_dict
        self.player = player

        self._set_grid_pos()
        self._init_bullet()

        self.isKill = False

    def _set_grid_pos(self):
        self.grid_x = int(self.pos2D.x // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]
        self.grid_y = int(self.pos2D.y // GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]
        self.grid_pos = self.grid_y * GRID_CONFIG["number_of_cells_w"] + self.grid_x
        self.spatial_grid_dict[self.grid_pos][self.uuid] = self

    def _update_grid_pos(self):
        new_grid_x = int(self.pos2D.x // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]
        new_grid_y = int(self.pos2D.y // GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]
        if new_grid_x != self.grid_x or new_grid_y != self.grid_y:
            del self.spatial_grid_dict[self.grid_pos][self.uuid]
            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            self.grid_pos = self.grid_y * GRID_CONFIG["number_of_cells_w"] + self.grid_x
            self.spatial_grid_dict[self.grid_pos][self.uuid] = self

    def _init_bullet(self):
        self.phy_damage = BULLET_CONFIG[self.bullet_type][1].get("physical_damage", 0)
        self.exp_damage = BULLET_CONFIG[self.bullet_type][1].get("explosion_damage", 0)
        self.bur_damage = BULLET_CONFIG[self.bullet_type][1].get("burn_damage", 0)
        self.speed = BULLET_CONFIG[self.bullet_type][1].get("speed", 0)
        self.radius = BULLET_CONFIG[self.bullet_type][1].get("radius", 0)
        self.lifetime = BULLET_CONFIG[self.bullet_type][1].get("lifetime", self.lifetime)

        self.explosion_radius = BULLET_CONFIG[self.bullet_type][1].get("explosion_radius", 0)
        for get_card in self.card_list:
            if get_card.type == 1:
                get_card.run_on_bullet(self)
            
        if self.vel2D.length() != 0:
            self.vel2D = self.vel2D.normalize() * self.speed * 30
        pass
    
    def draw(self, surface : pygame.Surface, to_screen : bool):
        draw_info = BULLET_CONFIG[self.bullet_type][1].get("draw_info", {})
        for key, value in draw_info.items():
            if key == "circle":
                for circle in value:
                    draw_pos = to_screen(self.pos2D)
                    if draw_pos.x < -circle["radius"] or draw_pos.x > surface.get_size()[0] + circle["radius"]:
                        continue
                    if draw_pos.y < -circle["radius"] or draw_pos.y > surface.get_size()[1] + circle["radius"]:
                        continue
                    pygame.draw.circle(surface, circle["color"], draw_pos, int(circle["radius"]))
            elif key == "line":
                for line in value:
                    start_pos = to_screen(self.pos2D)
                    end_pos = to_screen(self.pos2D + self.vel2D * 0.1)
                    pygame.draw.line(surface, line["color"], start_pos, end_pos, int(line["width"]))

    def get_damage(self, phy_multiplier : float = 1, exp_multiplier : float = 1, bur_multiplier : float = 1):
        return self.phy_damage * phy_multiplier + self.exp_damage * exp_multiplier + self.bur_damage * bur_multiplier
    
    def update(self, delta_time):
        old_vel = pygame.Vector2(self.vel2D)
        self.vel2D = self.vel2D + self.acc2D * delta_time
        self.pos2D = self.pos2D + (old_vel + self.vel2D) * 0.5 * delta_time

        self._update_grid_pos()

        if self.timer > self.lifetime:
            self.triger_lifetime()

        self.timer += delta_time

    def _explode(self):
        total_damage = 0
        radius = self.explosion_radius * self.multiplier
        radius_grid = int((radius // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]) + 1

        for i in range(self.grid_x - radius_grid, self.grid_x + radius_grid + 1):
            for j in range(self.grid_y - radius_grid, self.grid_y + radius_grid + 1):
                grid_x = i % GRID_CONFIG["number_of_cells_w"]
                grid_y = j % GRID_CONFIG["number_of_cells_h"]
                grid_pos = grid_y * GRID_CONFIG["number_of_cells_w"] + grid_x
                for entity in self.spatial_grid_dict[grid_pos].values():
                    if entity.entity_type != ENTITY_TYPE["enemy"]:
                        continue
                    if self.pos2D.distance_to(entity.pos2D) - entity.radius < radius:
                        damage = self.get_damage() * self.player.damage_multiplier * self.multiplier
                        total_damage += damage
                        entity.take_damage(damage)
                        self.hit_enemies.add(entity.uuid)
        self.player.add_damage_dealt(total_damage)

    def _hit(self, entity):
        if hasattr(entity, "take_damage"):
            damage = self.get_damage() * self.player.damage_multiplier * self.multiplier
            entity.take_damage(damage)
            self.player.add_damage_dealt(damage)
        if hasattr(entity, "uuid"):
            self.hit_enemies.add(entity.uuid)

    def _explode_effect(self, draw_type, effect_queue = None):
        radius = self.explosion_radius * self.multiplier
        if effect_queue is not None:
            if "explode" in draw_type:
                effect_queue.append([{"disappearing_circle" : [{ "pos_2D" : self.pos2D, "radius" : radius, "color" : (255, 200, 0, 255), "total_time" : 0.5 }]}, 0.5])

    def triger_hit(self, target_entity, effect_queue = None):
        if self.isKill == True:
            return

        self.status = 0
        self.last_hit_target = target_entity

        info = {"bullet" : self, "state" : -1}
        if self.bullet_type == 0 or self.bullet_type == 1 or self.bullet_type == 2:
            self._hit(target_entity)
            self.isKill = True
        elif self.bullet_type == 3: # Grenade
            self._explode()
            self._explode_effect("explode", effect_queue)
            self.isKill = True
        elif self.bullet_type == 4: # Laser
            self._hit(target_entity)

        

    def triger_lifetime(self, effect_queue = None):
        if self.bullet_type == 3: # Grenade
            self._explode()
            self._explode_effect("explode", effect_queue)
            self.isKill = True
        else:
            self.isKill = True
        
        self.status = 1

    def triger_time(self, ):
        self.status = 2


'''
-(Attribute Modifier) 屬性修正 ->
    - 這些 modifier 都會直接附加給 Gun 上，與 bullet 無關
    - 基本屬性 ->
        - 散射角 -20 -10 -5 +5 +10 +20
        - 發射間隔冷卻 -0.1 -0.2 -0.4
        - 換彈時間 -0.5 -1 -2
        - 子彈容量 +5 +10 +20
'''
class AttributeModifier():
    def __init__(self, type, value : int):
        pass

'''
- (Effect Modifier)特性修正 ->
	- 加成 (Bonus) ->
		- 速度傷害加成，傷害修正將加上子彈本身的最終速度數值的一半，每個子彈只能被加成一次
		- 傷害速度加成，速度修正將加上子彈本身的最終傷害數值的一半，每個子彈只能被加成一次
		- 散射角傷害加成，傷害修正將加上子彈本身的最終散射角數值的一半，每個子彈只能被加成一次
	- 能力 (Ability) ->
		- 命中敵人後的特性，可以用觸發修正來修正這個觸發條件
		- 每顆子彈最多只能疊加三次特性修正
		- Spilt（分裂）
			- 子彈碰撞到敵人後將會分裂成兩個，但分別往射擊方向+- 30度的散射角移動，且最終傷害砍半。
		- Penetrating（穿透）
			- 使子彈的穿透 +1
		- Explosive（爆炸彈）
			- 子彈對命中敵人周圍產生爆炸傷害，半徑為 20
		- Incendiary（燃燒彈）
			- 子彈命中敵人會對敵人產生灼傷傷害，灼傷傷害量與最終的傷害量成正比
		- (Poison Bullet（毒彈）) 會做不完，所以先不要毒
			- 子彈命中敵人會 +1 毒傷層數
		- Electric Bullet（電擊彈）
			- 子彈命中敵人會麻痺敵人，半徑為 20，麻痺 0.1 秒 (麻痺會傳播，所以範圍會比冰凍彈大，但是冰凍彈能夠使敵人停止得較久)
		- Freeze Bullet（冰凍彈）
			- 子彈命中敵人會冰凍敵人，半徑為 20，冰凍 0.4 秒，但減半最終的
		- Bounce Bullet（反彈彈）
			- 子彈碰撞到障礙物後會發生反彈
'''
class EffectModifier():
    def __init__(self, type):
        pass
    

