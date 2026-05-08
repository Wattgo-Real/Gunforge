
import pygame

from collections import deque
from Asset.GameSetting import GAME_CONFIG
from Asset.Weapons import Gun
from Asset.Card import Card
import random

class Player:
    def __init__(self, position : pygame.Vector2 = pygame.Vector2(0,0), radius : int = 10, color : tuple = (255, 255, 255),
                        max_velocity : float = 300, max_acceleration : float = 10000):
        self.pos2D : pygame.Vector2 = pygame.Vector2(position)
        self.vel2D : pygame.Vector2 = pygame.Vector2(0, 0)
        self.acc2D : pygame.Vector2 = pygame.Vector2(0, 0)

        self.max_velocity : float = max_velocity
        self.max_acceleration : float = max_acceleration

        self.radius : int = radius
        self.color : tuple = color
        self.mass : float = radius*radius

        # The direction the player is facing, it should always be normalized
        self.face_direction : pygame.Vector2 = pygame.Vector2(1, 0)
        self.inventory : list[Card | None] = [Card(type = 0, bullet_type = i) for i in range(5)] + \
                                            [Card(type = 2, effect_modifier_type = 0)] + \
                                            [Card(type = 2, effect_modifier_type = 100)] + \
                                            [None for i in range(20)]

        # weapon
        basic_info = {
            "cooldown" : 0.4,
            "reload" : 2,
            "scatter_angel" : 5,
            "capacity" : 20,
            "max_slots" : 20,
            "card_list" : [Card(type = 1, attribute_modifier_type = 9)] + 
                          [Card(type = 0, bullet_type = 0)] + 
                          [Card(type = 2, effect_modifier_type = i) for i in range(1)] + 
                          [Card(type = 2, effect_modifier_type = 100)] + 
                          [Card(type = 2, effect_modifier_type = 50), Card(type = 2, effect_modifier_type = 54)]
        }
        basic_info2 = {
            "cooldown" : 0.4,
            "reload" : 2,
            "scatter_angel" : 5,
            "capacity" : 20,
            "max_slots" : 20,
            "card_list" : [Card(type = 0, bullet_type = 0)],
        }

        self.weapon_list : list[Gun | None] = [Gun(basic_info), Gun(basic_info2), None, None]
        self.weapon_index : int = 0

        # This is for the player to record its trajectory
        self.history_position : deque = deque(maxlen=50)
        self.total_frame_passed : int = 0

        # Combat / progression stats
        self.max_hp : float = GAME_CONFIG["player_max_hp"]
        self.hp : float = self.max_hp
        self.invincible_timer : float = 0.0
        self.alive : bool = True

        self.xp : int = 0
        self.level : int = 1
        self.xp_to_next : int = GAME_CONFIG["xp_per_level_base"]

        # Run-time stat modifiers (granted by altars)
        self.damage_multiplier : float = 1.0
        self.bonus_speed : float = 0.0

        # Stat tracking (for end-of-run summary)
        self.kills : int = 0
        self.damage_dealt : float = 0.0
        self.points : int = 0
        
        # Dash mechanic
        self.dash_cooldown : float = 5.0
        self.dash_cooldown_timer : float = 0.0
        self.dash_duration : float = 0.2
        self.dash_timer : float = 0.0
        self.dash_speed_boost : float = 600.0  # Added to max velocity
        self.dash_acc_boost : float = 20000.0 # Added to max acceleration
        
        # Weapon feedback
        self.weapon_error_msg : str = ""
        self.weapon_error_timer : float = 0.0

    def get_velocity(self):
        '''
        Returns the velocity of the player
        '''
        return pygame.Vector2(self.vel2D).length()
    
    def get_acceleration(self):
        '''
        Returns the acceleration of the player
        '''
        return pygame.Vector2(self.acc2D).length()

    def set_position(self, pos2D):
        '''
        This is for the player to set its position
        '''
        self.pos2D = pygame.Vector2(pos2D)

    def set_velocity(self, vel_vec):
        '''
        This is for the player to set its velocity
        '''
        self.vel2D = pygame.Vector2(vel_vec)

        # Limit maximum speed
        if self.vel2D.length() > self.max_velocity:
            self.vel2D.scale_to_length(self.max_velocity)

    def set_acceleration(self, acc_vec):
        '''
        This is for the player to accelerate
        '''
        next_acc2D = pygame.Vector2(acc_vec)

        # Limit maximum acceleration
        if next_acc2D.length() > self.max_acceleration:
            next_acc2D.scale_to_length(self.max_acceleration)
        
        self.acc2D = next_acc2D

    def get_vel_orientation_deg(self):
        '''
        Get the angle of its velocity 

        Pygame's angle is 0 degrees pointing to the right (1, 0)
        '''
        if self.vel2D.length() == 0: 
            return 0
        
        # Vector2.as_polar() returns (length, angle).
        return self.vel2D.as_polar()[1]

    def get_acc_orientation_deg(self):
        '''
        Get the angle of its acceleration 

        Pygame's angle is 0 degrees pointing to the right (1, 0)
        '''
        if self.acc2D.length() == 0: 
            return 0
        
        return self.acc2D.as_polar()[1]

    def Update(self, delta_time : float, acc_direction : pygame.Vector2 = None):
        '''
        Update the position and velocity of the player, if acc_direction is None, 
        the player will stop with a reverse acceleration.

        Args:
            delta_time (float): The time step, e.g. 1/60
            acc_direction (pygame.Vector2): The direction of the acceleration
        '''
        # If the acceleration direction is not None and its length is greater than 0
        if acc_direction is not None and acc_direction.length_squared() > 0:
            acc_vector = acc_direction.normalize() * self.max_acceleration
            self.set_acceleration(acc_vector)
        else:
            # If the velocity is greater than 0
            if self.vel2D.length_squared() > 0:
                # 1. Determine the direction of deceleration (the opposite direction of velocity)
                friction_dir = -self.vel2D.normalize()
                
                # 2. Calculate the amount of velocity that will be reduced if the player accelerates with full force
                braking_force = self.max_acceleration * delta_time
                
                # 3. Prevent over-deceleration (Oversteer/Jitter)
                # If the current velocity is less than the velocity that can be reduced in this frame, set it directly to 0
                if self.vel2D.length() <= braking_force:
                    self.vel2D = pygame.Vector2(0, 0)
                    acc_vector = pygame.Vector2(0, 0)
                # Otherwise, apply the same magnitude of reverse acceleration as acceleration
                else:
                    acc_vector = friction_dir * self.max_acceleration
            else:
                # Already stopped
                acc_vector = pygame.Vector2(0, 0)
        self.set_acceleration(acc_vector)

        # Handle Dash Speed Boost
        current_max_vel = self.max_velocity
        current_max_acc = self.max_acceleration

        if self.dash_timer > 0:
            current_max_vel += self.dash_speed_boost
            current_max_acc += self.dash_acc_boost

        old_vel = pygame.Vector2(self.vel2D)

        # Update speed: v = v0 + a * dt
        new_vel = self.vel2D + self.acc2D * delta_time
        
        # Manually apply velocity limit here because set_velocity uses self.max_velocity
        if new_vel.length() > current_max_vel:
            new_vel.scale_to_length(current_max_vel)
        self.vel2D = new_vel

        # Update position: p = p0 + (v0 + v1)/2 * dt
        self.pos2D += (old_vel + self.vel2D) * 0.5 * delta_time

        # Record trajectory
        self.total_frame_passed += 1
        if self.total_frame_passed % 10 == 0:
            self.history_position.append(pygame.Vector2(self.pos2D))

    def UpdateWeapon(self, delta_time : float, fire : bool = False, trigger_feedback : bool = False):
        '''
        Update the weapon.

        Args:
            delta_time (float): The time step, e.g. 1/60
            fire (bool): Whether to fire
            trigger_feedback (bool): Whether to trigger feedback messages
        '''

        for i, weapon in enumerate(self.weapon_list):
            if weapon is None:
                continue

            if i == self.weapon_index:
                if fire:
                    res = weapon.fire(self.face_direction, self.pos2D)
                    if res != "" and trigger_feedback:
                        self.weapon_error_msg = res
                        self.weapon_error_timer = 0.5
            else:
                weapon.fire(pygame.Vector2(1, 0).rotate(random.random() * 360), self.pos2D)
            weapon.update(delta_time)
                

    def take_damage(self, damage : float):
        if self.invincible_timer > 0 or not self.alive:
            return False
        self.hp -= damage
        self.invincible_timer = GAME_CONFIG["player_invincible_time"]
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return True

    def heal(self, amount : float):
        self.hp = min(self.max_hp, self.hp + amount)

    def update_timers(self, delta_time : float):
        if self.invincible_timer > 0:
            self.invincible_timer = max(0.0, self.invincible_timer - delta_time)
        
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer = max(0.0, self.dash_cooldown_timer - delta_time)
        
        if self.dash_timer > 0:
            self.dash_timer = max(0.0, self.dash_timer - delta_time)
        
        if self.weapon_error_timer > 0:
            self.weapon_error_timer = max(0.0, self.weapon_error_timer - delta_time)

    def dash(self):
        '''
        Trigger the dash burst if cooldown is ready.
        '''
        if self.dash_cooldown_timer <= 0:
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            return True
        return False

    def gain_xp(self, value : int):
        self.xp += value
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(GAME_CONFIG["xp_per_level_base"] * (self.level ** 1.4))
            leveled = True
        return leveled

    def apply_altar_buff(self, buff_type : str):
        amounts = GAME_CONFIG["altar_buff_amount"]
        if buff_type == "hp":
            self.max_hp += amounts["hp"]
            self.hp += amounts["hp"]
        elif buff_type == "damage":
            self.damage_multiplier += amounts["damage"]
        elif buff_type == "speed":
            self.bonus_speed += amounts["speed"]
            self.max_velocity += amounts["speed"]

    def add_kill(self, damage_overflow : float = 0.0):
        self.kills += 1
        self.points += 1

    def add_damage_dealt(self, dmg : float):
        self.damage_dealt += dmg

    def reset_run(self, position : pygame.Vector2 = pygame.Vector2(0, 0)):
        self.pos2D = pygame.Vector2(position)
        self.vel2D = pygame.Vector2(0, 0)
        self.acc2D = pygame.Vector2(0, 0)
        self.hp = self.max_hp
        self.invincible_timer = 0.0
        self.alive = True
        self.xp = 0
        self.level = 1
        self.xp_to_next = GAME_CONFIG["xp_per_level_base"]
        self.kills = 0
        self.damage_dealt = 0.0
        self.points = 0
        self.dash_cooldown_timer = 0.0
        self.dash_timer = 0.0
        self.weapon_error_msg = ""
        self.weapon_error_timer = 0.0
        self.history_position.clear()
