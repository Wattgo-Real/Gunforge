
import pygame

from collections import deque
from Asset.Weapons import Gun

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

        # weapon
        self.weapon_list : list[Gun] = [Gun()]
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
            if i == self.weapon_index:
                if fire:
                    weapon.fire(self.face_direction, self.pos2D)
            else:
                pass
            weapon.update(delta_time)

