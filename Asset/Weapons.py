

import pygame
from collections import deque
import random

from Asset.GameSetting import BULLET_CONFIG, ATTRIBUTE_MODIFIER_CONFIG, EFFECT_MODIFIER_CONFIG, COLOR_CONFIG, GRID_CONFIG
from Asset.GameSetting import ENTITY_TYPE
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Asset.Card import Card
    #from Asset.Enemies import Enemy
    
import uuid

class Gun():
    def __init__(self, basic_info : dict, spatial_grid_dict = None):
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

        # Bullet's default attributes
        self.bullet_lifetime = 1.5  # How long the bullet will stay alive

        self.bullets = pygame.sprite.Group()
        self.cooldown_timer = 0     # Timer for bullet cooldown
        self.reload_timer = 0       # Timer for reload

        # for spatial partitioning
        self.spatial_grid_dict = spatial_grid_dict

    
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
        for card in self.card_list:
            if card is None: continue
            if card.type == 0:  # bullet
                bullet_type = card.bullet_type
                break
            if card.type == 2:  # attribute_modifier
                cart_to_bullet.append(card)

        if bullet_type == -1:
            return "No bullet card equipped!"

        if self.cooldown_timer == 0 and self.reload_timer == 0: 
            if self.capacity_left == 0:
                self.capacity_left = self.capacity
            if self.capacity_left <= 0:
                self.capacity_left = 0
                return "No bullet in clip!"

            direction = direction.rotate(random.uniform(-self.scatter_angel, self.scatter_angel))
            new_bullet = Bullet(cart_to_bullet, bullet_type, self.bullet_lifetime, pos2D, direction)
            self._add_bullet(new_bullet)
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

    def _add_bullet(self, bullet):
        self.bullets.add(bullet)
        grid_x = (bullet.pos2D.x // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]
        grid_y = (bullet.pos2D.y // GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]
        grid_pos = grid_y * GRID_CONFIG["number_of_cells_w"] + grid_x
        bullet.grid_pos = grid_pos
        self.spatial_grid_dict[grid_pos][bullet.uuid] = bullet
        

    def update(self, delta_time):
        self.cooldown_timer = max(0, self.cooldown_timer - delta_time)
        self.reload_timer = max(0, self.reload_timer - delta_time)

        for bullet in self.bullets:
            bullet.update(delta_time)

        # for spatial partitioning
        if self.spatial_grid_dict is not None:
            for bullet in self.bullets:
                grid_x = (bullet.pos2D.x // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]
                grid_y = (bullet.pos2D.y // GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]
                grid_pos = grid_y * GRID_CONFIG["number_of_cells_w"] + grid_x
                if grid_pos != bullet.grid_pos:
                    del self.spatial_grid_dict[bullet.grid_pos][bullet.uuid]
                    bullet.grid_pos = grid_pos
                    self.spatial_grid_dict[grid_pos][bullet.uuid] = bullet


class Bullet(pygame.sprite.Sprite):
    def __init__(self, card_list : list["Card"],
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

        self.uuid = uuid.uuid4()    # unique identifier of the spatial partitioning
        self.entity_type = ENTITY_TYPE["bullet"]

        self.card_list = card_list  # List of cards attached to the bullet
        self.lifetime = lifetime    # How long the bullet will stay alive
        self.timer = 0              # Timer for bullet lifetime
        self.bullet_type = bullet_type  # The type of bullet
        
        self.pos2D = pos2D        # The position of the bullet in 2D space
        self.vel2D = vel2D        # The velocity of the bullet in 2D space
        self.acc2D = acc2D        # The acceleration of the bullet in 2D space

        self.max_effect_count = 3
    
        self.hit_enemies = set()  # Track enemies already hit by this bullet
        self.init_bullet()

    def init_bullet(self):
        self.phy_damage = BULLET_CONFIG[self.bullet_type][1].get("physical_damage", 0)
        self.exp_damage = BULLET_CONFIG[self.bullet_type][1].get("explosion_damage", 0)
        self.bur_damage = BULLET_CONFIG[self.bullet_type][1].get("burn_damage", 0)
        self.speed = BULLET_CONFIG[self.bullet_type][1].get("speed", 0)
        self.radius = BULLET_CONFIG[self.bullet_type][1].get("radius", 0)
        self.lifetime = BULLET_CONFIG[self.bullet_type][1].get("lifetime", self.lifetime)

        self.explosion_radius = BULLET_CONFIG[self.bullet_type][1].get("explosion_radius", 0)

        effect_count = 0
        for card in self.card_list:
            card.run_on_bullet(self)
            if card.type == 2:
                effect_count += 1
                if effect_count >= self.max_effect_count:
                    break
            
        if self.vel2D.length() != 0:
            self.vel2D = self.vel2D.normalize() * self.speed
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

    def damage(self, phy_multiplier : float = 1, exp_multiplier : float = 1, bur_multiplier : float = 1):
        return self.phy_damage * phy_multiplier + self.exp_damage * exp_multiplier + self.bur_damage * bur_multiplier
    
    def update(self, delta_time):
        old_vel = pygame.Vector2(self.vel2D)
        self.vel2D = self.vel2D + self.acc2D * delta_time
        self.pos2D = self.pos2D + (old_vel + self.vel2D) * 0.5 * delta_time

        self.timer += delta_time

    def apply_card_effects(self):
        for card in self.card_list:
            if card.type == 2:
                pass

    def _explode(self, player, spatial_grid_dict):
        total_damage = 0
        radius_grid = int((self.explosion_radius // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"]) + 1
        bullet_grid_pos = [int(self.pos2D.x // GRID_CONFIG["cell_w"]) % GRID_CONFIG["number_of_cells_w"], 
                            int(self.pos2D.y // GRID_CONFIG["cell_h"]) % GRID_CONFIG["number_of_cells_h"]]

        for i in range(bullet_grid_pos[0] - radius_grid, bullet_grid_pos[0] + radius_grid + 1):
            for j in range(bullet_grid_pos[1] - radius_grid, bullet_grid_pos[1] + radius_grid + 1):
                grid_x = i % GRID_CONFIG["number_of_cells_w"]
                grid_y = j % GRID_CONFIG["number_of_cells_h"]
                grid_pos = grid_y * GRID_CONFIG["number_of_cells_w"] + grid_x
                for entity in spatial_grid_dict[grid_pos].values():
                    if entity.entity_type != ENTITY_TYPE["enemy"]:
                        continue
                    if self.pos2D.distance_to(entity.pos2D) - entity.radius < self.explosion_radius:
                        damage = self.damage() * player.damage_multiplier
                        total_damage += damage
                        entity.take_damage(damage)
                        self.hit_enemies.add(entity.uuid)
        player.add_damage_dealt(total_damage)

    def _hit(self, player, enemy):
        damage = self.damage() * player.damage_multiplier
        enemy.take_damage(damage)
        player.add_damage_dealt(damage)
        self.hit_enemies.add(enemy.uuid)

    def _explode_effect(self, draw_type, effect_queue = None):
        if effect_queue is not None:
            if "explode" in draw_type:
                effect_queue.append([{"disappearing_circle" : [{ "pos_2D" : self.pos2D, "radius" : self.explosion_radius, "color" : (255, 200, 0, 255), "total_time" : 0.5 }]}, 0.5])

    def triger_hit(self, player, target_enemy, effect_queue = None, spatial_grid_dict = None):
        if self.bullet_type == 0 or self.bullet_type == 1 or self.bullet_type == 2:
            self._hit(player, target_enemy)
            self.kill()
        elif self.bullet_type == 3: # Grenade
            self._explode(player, spatial_grid_dict)
            self._explode_effect("explode", effect_queue)
            self.kill()
        elif self.bullet_type == 4: # Laser
            if target_enemy.uuid not in self.hit_enemies:
                self._hit(player, target_enemy)
                
    def triger_lifetime(self, player, effect_queue = None, spatial_grid_dict = None):
        if self.bullet_type == 3: # Grenade
            self._explode(player, spatial_grid_dict)
            self._explode_effect("explode", effect_queue)
            self.kill()
        else:
            self.kill()

    def triger_time(self, ):
        pass

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
    

