

import pygame
from collections import deque
import random
import copy

from Asset.GameSetting import BULLET_CONFIG
from Asset.GameSetting import ENTITY_TYPE
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from Asset.Card import Card
    #from Asset.Enemies import Enemy
from Asset.SpatialGrid import SpatialGrid

import uuid

class Gun():
    def __init__(self, basic_info : dict, bullet_manager):
        '''
        Basic info of the gun
        '''
        self.basic_cooldown = basic_info["cooldown"]        # Time between shots
        self.basic_reload = basic_info["reload"]  # Time to reload
        self.basic_scatter_angle = basic_info["scatter_angle"]  # Degree of bullet spread
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
        self.scatter_angle = self.basic_scatter_angle
        self.capacity = self.basic_capacity

        self.multi_num = 1
        self.package = -1
        for card in self.card_list:
            if card:
                if card.type == 0:
                    if self.package == 0:
                        self.package = 1
                    elif self.package == 1:
                        card.run_on_gun(self)
                        self.package = -1
                    else:
                        self.multi_num -= 1
                        card.run_on_gun(self)
                else:
                    card.run_on_gun(self)

            if self.multi_num == 0 and self.package == -1:
                break


        if self.capacity_left > self.capacity:
            self.capacity_left = self.capacity
        if self.scatter_angle < 0:
            self.scatter_angle = 0
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
        card_to_bullet_list, bullet_inter_type_list = self._card_select()

        if bullet_inter_type_list == []:
            return "No bullet card equipped!"

        if self.cooldown_timer == 0 and self.reload_timer == 0:
            if self.capacity_left == 0:
                self.capacity_left = self.capacity
            if self.capacity_left <= 0:
                self.capacity_left = 0
                return "No bullet in clip!"


            for i, card_to_bullet in enumerate(card_to_bullet_list):
                direction = direction.rotate(random.uniform(-self.scatter_angle, self.scatter_angle))
                self.bullet_manager.add_bullet(card_to_bullet, bullet_inter_type_list[i], pos2D, direction)
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

    def _card_select(self):
        card_to_bullet_list = []
        bullet_inter_type_list = []

        card_to_bullet = []
        effect_card_count = 0
        multi_num = 1
        package = -1
        for i, card in enumerate(self.card_list):
            if card is None: continue
            if card.type == 0:  # bullet
                if package == 0:
                    bullet_inter_type_list.append(card.inter_type)
                    package = 1
                elif package == 1:
                    card_to_bullet.append(card)
                    card_to_bullet_list.append(card_to_bullet)
                    card_to_bullet = []
                    package = -1
                else:
                    bullet_inter_type_list.append(card.inter_type)
                    card_to_bullet_list.append(card_to_bullet)
                    card_to_bullet = []
                    multi_num -= 1

                if multi_num == 0 and package == -1:
                    break
                continue
            if card.type == 1:  # attribute
                if card.inter_type >= 50:
                    card_to_bullet.append(card)
                continue
            if card.type == 2:  # projectile
                if effect_card_count >= self.max_effect_count:
                    continue
                card_to_bullet.append(card)
                effect_card_count += 1
            if card.type == 3:  # trigger
                card_to_bullet.append(card)
            if card.type == 4:  # multibullet
                if card.inter_type == 0:    # "Package"
                    package = 0
                elif card.inter_type == 1:    # "multibullet"
                    multi_num += 1
                elif card.inter_type == 2:    # "multibullet"
                    multi_num += 2
                elif card.inter_type == 3:    # "multibullet"
                    multi_num += 3
            if card.type == 5:
                card_to_bullet.append(card)
        if package == 1:
            card_to_bullet_list.append(card_to_bullet)
            card_to_bullet = []

        return card_to_bullet_list, bullet_inter_type_list

    def update(self, delta_time):
        self.cooldown_timer = max(0, self.cooldown_timer - delta_time)
        self.reload_timer = max(0, self.reload_timer - delta_time)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, card_list : list["Card"],
                inter_type : int,
                player,
                spatial_grid_dict : SpatialGrid,
                pos2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                vel2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                acc2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                basic_info : dict = {},
                player_vel2D : pygame.Vector2 = None,
                hit_enemies : set = set()):
        '''
        inter_type:
            0, Normal Bullet
            1, Light Bullet
            2, Heavy Bullet
            3, Grenades
            4, Laser

        params:
            card_list (list) : List of cards that can be attached to this bullet
            lifetime (float) : How long the bullet will stay alive
            inter_type (str) : The type of bullet
            pos2D (pygame.Vector2) : The position of the bullet in 2D space
            vel2D (pygame.Vector2) : The velocity of the bullet in 2D space
            acc2D (pygame.Vector2) : The acceleration of the bullet in 2D space
        '''
        super().__init__()
        self.uuid = uuid.uuid4()    # unique identifier of the spatial partitioning
        self.entity_type = ENTITY_TYPE["bullet"]
        self.inter_type = inter_type  # The type of bullet

        self.pos2D = pos2D        # The position of the bullet in 2D space
        self.vel2D = vel2D        # The velocity of the bullet in 2D space
        self.acc2D = acc2D        # The acceleration of the bullet in 2D space
        self.hit_enemies = hit_enemies.copy()  # Track enemies already hit by this bullet
        self.multiplier = 1


        self.card_list : list[Card] = card_list  # List of cards attached to the bullet

        self.lifetime = 1.0   # How long the bullet will stay alive
        self.timer = 0        # Timer for bullet lifetime
        self.status = -1      # -1 nothing, 0 hit, 1 lifetime, 2 time
        self.trigger_type = 0 # 0: hit, 1: lifetime, 2: time


        self.spatial_grid_dict = spatial_grid_dict
        self.player = player
        if player_vel2D is None:
            self.player_vel2D = self.player.vel2D.copy()
        else:
            self.player_vel2D = player_vel2D.copy()

        self._set_grid_pos()
        self._init_bullet()

        self.isKill = False

    def _set_grid_pos(self):
        self.spatial_grid_dict.register_entity(self)

    def _update_grid_pos(self):
        self.grid_pos = self.spatial_grid_dict.update_entity_pos(self, self.grid_pos, self.pos2D)

    def _init_bullet(self):
        self.phy_damage = BULLET_CONFIG[self.inter_type][1].get("physical_damage", 0)
        self.exp_damage = BULLET_CONFIG[self.inter_type][1].get("explosion_damage", 0)
        self.bur_damage = BULLET_CONFIG[self.inter_type][1].get("burn_damage", 0)
        self.speed = BULLET_CONFIG[self.inter_type][1].get("speed", 0)
        self.radius = BULLET_CONFIG[self.inter_type][1].get("radius", 0)
        self.lifetime = BULLET_CONFIG[self.inter_type][1].get("lifetime", self.lifetime)

        self.explosion_radius = BULLET_CONFIG[self.inter_type][1].get("explosion_radius", 0)
        self.trajectory_modifier_list = []
        for get_card in self.card_list:
            get_card.run_on_bullet(self)

        if self.vel2D.length() != 0:
            self.vel2D = self.vel2D.normalize() * self.speed * 30 + self.player_vel2D

        # TODO: Need to find better way to set init_speed
        for trajectory_modifier in self.trajectory_modifier_list:
            if trajectory_modifier.inter_type == 4:
                trajectory_modifier.init_speed = self.vel2D.copy().normalize().rotate(-75) * 1000
            elif trajectory_modifier.inter_type == 7:
                trajectory_modifier.player = self.player
                trajectory_modifier.player_old_pos2D = self.player.pos2D.copy()
        pass

    def get_pos2D(self):
        return self.pos2D

    def update(self, delta_time):
        old_vel = pygame.Vector2(self.vel2D)
        self.vel2D = self.vel2D + self.acc2D * delta_time
        for trajectory_modifier in self.trajectory_modifier_list:
            self.pos2D, self.vel2D, self.acc2D = trajectory_modifier.run(self.pos2D, self.vel2D, self.acc2D, self.timer)
        self.vel2D = self.vel2D + self.acc2D * delta_time
        self.pos2D = self.pos2D + self.vel2D * delta_time

        self._update_grid_pos()

        if self.timer > self.lifetime:
            self.triger_lifetime()

        self.timer += delta_time
        if self.trigger_type >= 2:
            if self.timer > self.trigger_time:
                self.status = self.trigger_type


    def draw(self, surface : pygame.Surface, to_screen : bool):
        draw_info = BULLET_CONFIG[self.inter_type][1].get("draw_info", {})
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
        damage = self.phy_damage * phy_multiplier + self.exp_damage * exp_multiplier + self.bur_damage * bur_multiplier
        if getattr(self, "sd_card", False):
            if self.vel2D.length() != 0:
                damage += self.vel2D.length() / 30 / 2
        return damage

    def hit(self, entity):
        if hasattr(entity, "take_damage"):
            damage = self.get_damage(1,0,0) * self.player.damage_multiplier * self.multiplier
            entity.take_damage(damage)
            self.player.add_damage_dealt(damage)
        if hasattr(entity, "uuid"):
            self.hit_enemies.add(entity.uuid)

    def burn(self, entity):
        if hasattr(entity, "take_damage"):
            damage = self.get_damage(0,0,1) * self.player.damage_multiplier * self.multiplier
            entity.take_damage(damage)
            self.player.add_damage_dealt(damage)
        if hasattr(entity, "uuid"):
            self.hit_enemies.add(entity.uuid)

    def explode(self):
        total_damage = 0
        radius = self.explosion_radius * self.multiplier
        for entity in self.spatial_grid_dict.get_entities_in_radius(self.pos2D, radius, ENTITY_TYPE["enemy"]):
            if self.pos2D.distance_to(entity.pos2D) - entity.radius < radius:
                damage = self.get_damage(0,1,0) * self.player.damage_multiplier * self.multiplier
                total_damage += damage
                entity.take_damage(damage)
        self.player.add_damage_dealt(total_damage)

    def explode_effect(self, draw_type, effect_queue = None):
        radius = self.explosion_radius * self.multiplier
        if effect_queue is not None:
            if "explode" in draw_type:
                effect_queue.append([{"disappearing_circle" : [{ "pos_2D" : self.pos2D, "radius" : radius, "color" : (255, 200, 0, 255), "total_time" : 0.5 }]}, 0.5])

    def triger_hit(self, target_entity, effect_queue = None):
        if self.isKill == True:
            return

        self.last_hit_target = target_entity

        info = {"bullet" : self, "state" : -1}
        if self.inter_type == 0 or self.inter_type == 1 or self.inter_type == 2:
            self.hit(target_entity)
            self.isKill = True
        elif self.inter_type == 3: # Grenade
            self.explode()
            self.explode_effect("explode", effect_queue)
            self.isKill = True
        elif self.inter_type == 4: # Laser
            self.burn(target_entity)

        self.status = 0

    def triger_lifetime(self, effect_queue = None):
        if self.inter_type == 3: # Grenade
            self.explode()
            self.explode_effect("explode", effect_queue)
            self.isKill = True
        else:
            self.isKill = True

        self.status = 1

    def triger_time(self, effect_queue = None):
        self.status = 2

class BulletManager():
    def __init__(self, spatial_grid_dict : SpatialGrid):
        self.bullets = pygame.sprite.Group()
        self.spatial_grid_dict = spatial_grid_dict
        self.player = None

    def reset(self, spatial_grid_dict : SpatialGrid = None):
        self.bullets.empty()
        self.spatial_grid_dict = spatial_grid_dict

    def add_bullet(self, card_to_bullet, inter_type, pos2D, direction):
        new_bullet = Bullet(card_to_bullet, inter_type, self.player, self.spatial_grid_dict, pos2D, direction)
        self.bullets.add(new_bullet)
        return new_bullet

    def update(self, delta_time, effects_queue):
        for bullet in self.bullets:
            bullet.update(delta_time)
            if bullet.status == bullet.trigger_type:
                self.check_card_status(bullet, effects_queue)
                bullet.status = -1

            if bullet.isKill == True:
                self.spatial_grid_dict.remove_entity(bullet.grid_pos, bullet.uuid)
                bullet.kill()

    def check_card_status(self, bullet, effects_queue):
        remove_card = []
        for card in bullet.card_list:
            if card.type == 0:
                remove_card.append(card)

                new_cards = bullet.card_list.copy()
                new_cards.remove(card)
                card_to_bullet = new_cards
                inter_type = card.inter_type
                direction = bullet.vel2D
                pos2D = bullet.pos2D
                hit_enemies = bullet.hit_enemies

                new_bullet = Bullet(card_to_bullet, inter_type, self.player, self.spatial_grid_dict, pos2D, direction,
                                    player_vel2D = bullet.player_vel2D, hit_enemies = hit_enemies)
                self.bullets.add(new_bullet)
                break

            elif card.type == 2:
                remove_card.append(card)
                if card.inter_type < 2:   # Split
                    new_cards = bullet.card_list.copy()
                    new_cards.remove(card)
                    pos2D, vel2D, acc2D = bullet.pos2D, bullet.vel2D, bullet.acc2D
                    hit_enemies = bullet.hit_enemies

                    if card.inter_type == 0:
                        vel2D_v1 = vel2D.rotate(random.randint(-45, 45))
                        vel2D_v2 = vel2D.rotate(random.randint(-45, 45))
                    elif card.inter_type == 1:
                        vel2D_v1 = vel2D.rotate(random.randint(135, 225))
                        vel2D_v2 = vel2D.rotate(random.randint(135, 225))
                    elif card.inter_type == 2:
                        vel2D_v1 = vel2D
                        vel2D_v2 = vel2D

                    new_bullet = Bullet(new_cards, bullet.inter_type, self.player, self.spatial_grid_dict, pos2D, vel2D_v1, acc2D,
                                        player_vel2D = bullet.player_vel2D, hit_enemies = hit_enemies)
                    new_bullet.multiplier = bullet.multiplier * 0.5
                    self.bullets.add(new_bullet)

                    new_bullet = Bullet(new_cards, bullet.inter_type, self.player, self.spatial_grid_dict, pos2D, vel2D_v2, acc2D,
                                        player_vel2D = bullet.player_vel2D, hit_enemies = hit_enemies)
                    new_bullet.multiplier = bullet.multiplier * 0.5
                    self.bullets.add(new_bullet)

                    break

                elif card.inter_type == 2:    # Penetrate
                    bullet.isKill = False
                    new_cards = bullet.card_list.copy()
                    new_cards.remove(card)
                    bullet.card_list = new_cards

                    break

                elif card.inter_type == 3:  # Bounce
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

                elif card.inter_type == 4:  # Explode
                    bullet.explosion_radius += 40
                    bullet.exp_damage = bullet.get_damage() / 2
                    bullet.explode()
                    bullet.explode_effect("explode", effects_queue)
                    break

            elif card.type == 3:  #
                remove_card.append(card)

        bullet.card_list = [c for c in bullet.card_list if c not in remove_card]
