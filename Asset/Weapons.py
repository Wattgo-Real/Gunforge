
import pygame
from collections import deque

class Bullet(pygame.sprite.Sprite):
    def __init__(self, card_list : list,
                lifetime : float,
                pos2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                vel2D : pygame.Vector2 = pygame.math.Vector2(0,0),
                acc2D : pygame.Vector2 = pygame.math.Vector2(0,0)):
        '''
        params:
            card_list (list) : List of cards that can be attached to this bullet
            lifetime (float) : How long the bullet will stay alive
            pos2D (pygame.Vector2) : The position of the bullet in 2D space
            vel2D (pygame.Vector2) : The velocity of the bullet in 2D space
            acc2D (pygame.Vector2) : The acceleration of the bullet in 2D space
        '''
        super().__init__()
        
        self.card_list = card_list  # List of cards attached to the bullet
        self.lifetime = lifetime    # How long the bullet will stay alive
        self.timer = 0              # Timer for bullet lifetime

        self.pos2D = pos2D        # The position of the bullet in 2D space
        self.vel2D = vel2D        # The velocity of the bullet in 2D space
        self.acc2D = acc2D        # The acceleration of the bullet in 2D space

    def update(self, delta_time):
        old_vel = pygame.Vector2(self.vel2D)
        self.vel2D = self.vel2D + self.acc2D * delta_time
        self.pos2D = self.pos2D + (old_vel + self.vel2D) * 0.5 * delta_time

        self.timer += delta_time
        if self.timer >= self.lifetime:
            self.kill()

class Gun():
    def __init__(self):
        '''
        Basic info of the gun
        '''
        self.cooldown = 0.1         # Time between shots
        self.reload = 0.5           # Time to reload
        self.scatter_angel = 5      # Degree of bullet spread
        self.capacity = 30          # The maximum number of bullets the gun can hold
        self.card_max_slots = 5     # How many cards can this weapon hold?
        self.card_list = []         # List of cards attached to the gun

        # Bullet's default attributes
        self.bullet_lifetime = 1.5  # How long the bullet will stay alive
        self.bullet_vel = 500       # The velocity of the bullet
        
        self.capacity_left = self.capacity

        self.bullets = pygame.sprite.Group()
        self.cooldown_timer = 0     # Timer for bullet cooldown
        self.reload_timer = 0       # Timer for reload

    def fire(self, direction : pygame.Vector2, pos2D : pygame.Vector2): 
        if self.cooldown_timer == 0 and self.reload_timer == 0: 
            new_bullet = Bullet(self.card_list, self.bullet_lifetime, pos2D, direction * self.bullet_vel)
            self.bullets.add(new_bullet)
            self.cooldown_timer = self.cooldown

            # Reduce ammo in clip
            self.capacity_left -= 1
            if self.capacity_left == 0:
                self.capacity_left = self.capacity
                self.reload_timer = self.reload

    def update(self, delta_time):
        self.cooldown_timer = max(0, self.cooldown_timer - delta_time)
        self.reload_timer = max(0, self.reload_timer - delta_time)

        for bullet in self.bullets:
            bullet.update(delta_time)
        
