import pygame
from pygame.locals import *
import math
import os

from game_object import GameObject

distance = GameObject.setting[3]
Mask_image = pygame.image.load(os.path.join("images", "mask.png"))

class Bullet(GameObject):
    # master may be you or enemies
    def __init__(self, master, speed=30, power=1):
        super().__init__(master)
        self.x = master.x
        self.y = master.y
        self.r = 7
        self.angle = master.gun.angle + master.angle
        self.speed = speed
        self.color = master.color
        self.range = 700
        self.v = self.master.v.copy()
        self.move(self.angle, distance)
        self.power = power
    #口罩子彈
    def mask_repaint(self, screen, position):
        xy = super().repaint(screen, position)
        self.mask = pygame.transform.scale(Mask_image, (50, 50))
        self.image = self.mask
        screen.blit(self.image, (xy))
    #圓形子彈
    def repaint(self, screen, position):
        xy = super().repaint(screen, position)
        pygame.draw.circle(screen, self.color, xy, self.r)

    # 子彈的位移
    def move(self, angle, step):
        # step 就是子彈速度
        self.x += step * math.cos(angle)
        self.y += step * math.sin(angle)
        # 反作用力
        self.range -= step

    def update(self, touch):
        self.move(self.angle, self.speed)
        # super().update(f = 0.95)
        if self.range < 0 or touch(): 
            self.kill()
    # 這裡是空的是為了下面需要繼承
    def kill(self):
        pass

class PlayerBullet(Bullet):
    def repaint(self, screen, position,change):
        self.change = change
        #print(self.change)
        if self.change == 1:
            xy = super().repaint(screen, position)
        else:
            xy = super().mask_repaint(screen, position)
            self.mask = pygame.transform.scale(Mask_image, (50, 50))
            self.image = self.mask
    def update(self):
        f = lambda:self.master.master.field.touch(self) or self.master.master.monster.touch(self)
        super().update(f)

    def kill(self):
        self.master.bullet.remove(self)


class SniperBullet(Bullet):
    def __init__(self, master, speed=30):
        super().__init__(master, speed)
        self.score = 0
        self.color = [255, 255, 0]

    def update(self):
        f = lambda:self.master.field.touch(self)
        super().update(f)

    def kill(self):
        self.master.master.bullet.remove(self)
        self.master.master.update_live()
        
