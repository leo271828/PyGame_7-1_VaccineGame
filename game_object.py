import json
import pygame
import math
import random


pygame.init()
F = 0.88
setting = json.load(open('setting.json', 'r'))

class GameObject:
    setting = json.load(open('setting.json', 'r'))
    
    def __init__(self, master=None):
        self.master = master
        self.x = 0
        self.y = 0
        self.v = [0, 0]
        self.angle = 0
        self.color = []
        self.last_time = 0
        self.touchable = []

    def repaint(self, screen, position):
        return int(self.x - position[0] + self.setting['wh'][0]/2), \
        int(self.y - position[1] + self.setting['wh'][1]/2)

    def update(self,touch=lambda:None, f=F):
        if touch():
            self.live = False
        self.x += self.v[0]
        if touch():
            self.x -= self.v[0]
            self.v[0] = 0
        self.y += self.v[1]
        if touch():
            self.y -= self.v[1]
            self.v[1] = 0

        self.v = [x*f for x in self.v]

    def kill(self):
        pass
    
    @staticmethod
    def iskey(key):
        all_key = pygame.key.get_pressed()
        return all_key[key]
    
    def delay(self, time):
        return True if pygame.time.get_ticks() - self.last_time > time else False
    def near(self, position, step):
        x, y = self.x-position[0], self.y-position[1]
        distance = (x ** 2 + y ** 2) ** 0.5
        self.v[0] -= x/distance * step
        self.v[1] -= y/distance * step

    def move(self, angle, step):
        self.v[0] += step * math.cos(angle)
        self.v[1] += step * math.sin(angle)

    def touch(self, person):
        distance = ((person.x - self.x)**2 + (person.y - self.y)**2) ** 0.5
        return self if distance < self.r+person.r else None

    @staticmethod
    def map(ah, al, bh, bl, c):
        a = ah - al
        b = bh - bl
        return (c - al) / a * b + bl


class Manager(GameObject):
    def __init__(self, master):
        self.master = master
        self.player = master.player
        self.last_time = 0
        self.live = []

    def repaint(self, screen, position):
        for i in self.live:
            i.repaint(screen, position)

    def update_live(self, be_live = []):
        p = self.player
        self.live = [i for i in be_live if ((i.x-p.x)**2+(i.y-p.y)**2) ** 0.5 < 2000]

    def touch(self, person):
        for i in self.live:
            if i.touch(person) and person is not z:
                return i
        else:
             return None

    def update(self, be_kill=[]):
        if be_kill:
            for i in be_kill:
                if i not in self.live:
                    i.kill()
                    break

