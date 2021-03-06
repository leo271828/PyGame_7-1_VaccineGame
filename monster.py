import pygame
from pygame.locals import *
import math
import random
import os

from game_object import *
from player import SniperGun
from bullet import SniperBullet

# 匯入圖片
Sick_person = pygame.image.load(os.path.join("images", "sick_person.png"))
enemy_easy = pygame.image.load(os.path.join("images", "enemy_easy.png"))
enemy_middle = pygame.image.load(os.path.join("images", "enemy_middle.png"))
enemy_hard = pygame.image.load(os.path.join("images", "enemy_hard.png"))


# 敵人數量
z_capped = lambda x: 10 + x*2
s_capped = lambda x: 50 + x*5


class MonsterManager(Manager):
    def __init__(self, master):
        self.master = master
        self.last_time = 0
        self.player = master.player
        self.zombies = []
        self.snipers = []
        self.bullet = []
        self.live = []
        self.color = [0, 255, 255]

    def update(self):
        if pygame.time.get_ticks() - self.last_time > 1000:
            self.update_live()
            super().update(self.zombies + self.snipers)
            self.last_time = pygame.time.get_ticks()
        elif len(self.zombies) < z_capped(self.player.level):
            self.zombies.append(Zombie(self))
        elif len(self.snipers) < s_capped(self.player.level):
            self.snipers.append(Sniper(self))
        for z in self.live + self.bullet:
            z.update()

    def touch(self, person, mode=True):
        for z in self.live:
            if z.touch(person):
                return z
        if mode:
            for b in self.bullet:
                if b.touch(person):
                    return b
        return None

    def update_live(self):
        super().update_live(self.zombies + self.snipers)

    def repaint(self, screen, position):
        for i in self.live + self.bullet:
            i.repaint(screen, position)


class Monster(GameObject):
    '''怪物的父類別'''

    def __init__(self, master, position=None, color=None):
        super().__init__(master)
        self.player = master.player
        self.field = self.master.master.field
        self.speed = 1
        self.angle = 0
        self.color = [0, 0, 255]
        self.r = enemy_wh[0]//2
        self.live = True
        self.blood = 1.0
        self.power = 1.0
        self.range = lambda: 600  > self.distance(self)
        # 圖片
        self.person = pygame.transform.scale(Sick_person, enemy_wh)
        self.enemy_easy = pygame.transform.scale(enemy_easy, enemy_wh)
        self.enemy_middle = pygame.transform.scale(enemy_middle, enemy_wh)
        self.enemy_hard = pygame.transform.scale(enemy_hard, enemy_wh)

        self.image = self.person

        if position:
            self.x, self.y = position
        else:
            w, h = self.setting[4]
            self.x = random.randint(-w + 1000, w - 1000)
            self.y = random.randint(-h + 1000, h - 1000)
        if self.field.touch(self, True):
            self.live = False
            self.color = [255, 255, 0]

    def repaint(self, screen, position):
        x,y = super().repaint(screen, position)
        screen.blit(self.image, (x - enemy_wh[0] // 2,y - enemy_wh[1]//2))

    def move(self, angle, step):
        self.x += step * math.cos(angle)
        if self.field.touch(self):
            self.x -= step * math.cos(angle)
        self.y += step * math.sin(angle)
        if self.field.touch(self):
            self.y -= step * math.sin(angle)

    def near(self, position, step):
        x, y = self.x - position[0], self.y - position[1]
        distance = (x ** 2 + y ** 2) ** 0.5
        self.v[0] -= x / distance * step
        self.v[1] -= y / distance * step

    def touch(self, person):
        if person is self:
            return None
        d = self.distance(person)
        result = self if d < self.r + person.r else None
        if person in self.player.bullet and result:
            self.hit(person.power)
            self.near((person.x, person.y), -20)
        return result

    def distance(self, person):
        return ((person.x - self.x) ** 2 + (person.y - self.y) ** 2) ** 0.5

    def hit(self, power):
        self.blood -= power
        if self.blood <= 0:
            self.live = False


class Zombie(Monster):
    def __init__(self, master):
        super().__init__(master)
        self.speed = 0.75
        self.monster_key = 2

    # 更換圖片
    def repaint(self, screen, position):
        super().repaint(screen, position)
        self.image = self.person

    def update(self):
        if self.range():
            self.near((self.player.x, self.player.y), self.speed)
        super().update(lambda: self.field.touch(self) or self.master.touch(self, False))
        if not self.live:
            self.kill()

    def hit(self, power):
        # 判斷子彈跟怪物是否一樣
        self.key = self.player.get()
        if self.key == self.monster_key:
            super().hit(power)

    def kill(self):
        self.master.zombies.remove(self)
        self.master.update_live()


class Sniper(Monster):
    def __init__(self, master):
        super().__init__(master)
        self.speed = 1.5
        self.gun = SniperGun(self)  # 改成 SniperGun
        self.angle = 0
        self.shuting = True
        self.gun.shuting = True
        self.monster_key = 1

    def repaint(self, screen, position):
        super().repaint(screen, position)
        self.gun.repaint(screen, position)
        # 更換圖片
        self.image = self.enemy_easy

    def update(self):
        x, y = self.x - self.player.x, self.y - self.player.y
        self.angle = math.atan(y / x)
        if x > 0:
            self.angle += math.pi
            pass
        d = (x ** 2 + y ** 2) ** 0.5
        if self.range():
            if d > 600:
                self.near((self.player.x, self.player.y), self.speed)
            elif pygame.time.get_ticks() - self.last_time > 1300:
                self.master.bullet.append(SniperBullet(self, 20))
                self.master.update_live()
                self.last_time = pygame.time.get_ticks()
            elif d < 400:
                self.near((self.player.x, self.player.y), -self.speed)
            super().update(lambda: self.field.touch(self) or self.master.touch(self, False))
            self.gun.update()
        if not self.live:
            self.kill()

    def hit(self, power):
        # 判斷子彈跟怪物是否一樣
        self.key = self.player.get()
        if self.key == self.monster_key:
            # 亂數增加疫苗
            self.player.addvaccine(random.randint(1, 6))
            super().hit(power)

    def kill(self):
        self.master.snipers.remove(self)
        self.master.update_live()
        self.gun = None
