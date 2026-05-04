
import pygame

from collections import deque
from Asset.Weapons import Gun, Card

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
        self.inventory : list[Card | None] = [None for i in range(40)]

        # weapon
        basic_info = {
            "cooldown" : 0.4,
            "reload" : 2,
            "scatter_angel" : 5,
            "capacity" : 20,
            "card_list" : [Card(type = 1, attribute_modifier_type = 0), Card(type = 1, attribute_modifier_type = 1), 
                            Card(type = 1, attribute_modifier_type = 2), Card(type = 1, attribute_modifier_type = 3), 
                            Card(type = 1, attribute_modifier_type = 4), Card(type = 1, attribute_modifier_type = 5), 
                            Card(type = 1, attribute_modifier_type = 6), Card(type = 1, attribute_modifier_type = 7), 
                            Card(type = 0, bullet_type = 0), Card(type = 0, bullet_type = 1), Card(type = 0, bullet_type = 2)],
        }

        self.weapon_list : list[Gun | None] = [Gun(basic_info), None, None, None]
        self.weapon_index : int = 0

        # This is for the player to record its trajectory
        self.history_position : deque = deque(maxlen=50)
        self.total_frame_passed : int = 0

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

        old_vel = pygame.Vector2(self.vel2D)

        # Update speed: v = v0 + a * dt
        new_vel = self.vel2D + self.acc2D * delta_time
        self.set_velocity(new_vel)

        # Update position: p = p0 + (v0 + v1)/2 * dt
        self.pos2D += (old_vel + self.vel2D) * 0.5 * delta_time

        # Record trajectory
        self.total_frame_passed += 1
        if self.total_frame_passed % 10 == 0:
            self.history_position.append(pygame.Vector2(self.pos2D))

    def UpdateWeapon(self, delta_time : float, fire : bool = False):
        '''
        Update the weapon.

        Args:
            delta_time (float): The time step, e.g. 1/60
            fire (bool): Whether to fire
        '''

        for i, weapon in enumerate(self.weapon_list):
            if weapon is None:
                continue

            if i == self.weapon_index:
                if fire:
                    weapon.fire(self.face_direction, self.pos2D)
            else:
                pass
            weapon.update(delta_time)

class Enemy:
    def __init__(self, position: pygame.Vector2, radius: int = 30, color: tuple = (255, 50, 50), hp: int = 1000):
        self.pos2D = pygame.Vector2(position)
        self.radius = radius
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.damage_numbers = [] # List of DamageNumber objects

    def take_damage(self, damage):
        self.hp -= damage
        # Create a new damage number effect
        self.damage_numbers.append(DamageNumber(damage, self.pos2D.copy()))

    def update(self, delta_time):
        for dn in self.damage_numbers[:]:
            dn.update(delta_time)
            if dn.timer <= 0:
                self.damage_numbers.remove(dn)

    def draw(self, screen, game):
        # Draw enemy body
        screen_pos = game.to_screen(self.pos2D)
        pygame.draw.circle(screen, self.color, screen_pos, self.radius)
        pygame.draw.circle(screen, (255, 255, 255), screen_pos, self.radius, 2)
        
        # Draw health bar (optional but useful)
        bar_w = 60
        bar_h = 6
        pygame.draw.rect(screen, (50, 50, 50), (screen_pos.x - bar_w//2, screen_pos.y - self.radius - 15, bar_w, bar_h))
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (100, 255, 100), (screen_pos.x - bar_w//2, screen_pos.y - self.radius - 15, int(bar_w * hp_ratio), bar_h))

        # Draw damage numbers
        for dn in self.damage_numbers:
            dn.draw(screen, game)

class DamageNumber:
    def __init__(self, damage, position):
        self.damage = damage
        self.pos2D = position + pygame.Vector2(pygame.math.Vector2(0, 20).rotate(pygame.math.Vector2(0, 0).angle_to(pygame.math.Vector2(1,0)) + (pygame.time.get_ticks() % 360))) # Randomize slightly
        # Actually just a simple random offset
        import random
        self.pos2D += pygame.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
        self.velocity = pygame.Vector2(0, 50) # Float upwards
        self.timer = 1.0 # Stay for 1 second
        self.alpha = 255

    def update(self, delta_time):
        self.pos2D.y += self.velocity.y * delta_time
        self.timer -= delta_time
        self.alpha = int(255 * (self.timer / 1.0))

    def draw(self, screen, game):
        font = game.HUD_font
        text_surf = font.render(str(int(self.damage)), True, (255, 255, 100))
        # Handle alpha if needed (requires temporary surface)
        text_surf.set_alpha(self.alpha)
        screen_pos = game.to_screen(self.pos2D)
        screen.blit(text_surf, (screen_pos.x - text_surf.get_width()//2, screen_pos.y))
