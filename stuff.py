import pygame
from pygame.locals import *
import random

from game_object import *


h_capped = 70
s_capped = 300

class StuffManager(Manager):
    def __init__(self, master):
        super().__init__(master)
        self.hearts = []
        self.stars = []

    def repaint(self, screen, position):
        for h in self.live:
            h.repaint(screen, position)

    def update(self):
        if self.delay(1000):
            self.update_live()
            super().update(self.hearts+self.stars)
            self.last_time = pygame.time.get_ticks()
        elif len(self.hearts) < h_capped:
            self.hearts.append(Heart(self))
        elif len(self.stars) < s_capped:
            self.stars.append(Star(self))
        for a in self.live:
            a.update()

    def update_live(self):
        super().update_live(self.hearts+self.stars)


class Stuff(GameObject):
    def __init__(self, master):
        super().__init__(master)
        self.r = 10
        w, h = self.setting['field_wh']
        self.x = random.randint(-w+1000, w-1000)
        self.y = random.randint(-h+1000, h-1000)
        self.player = self.master.master.player
        if self.master.master.field.touch(self, True):
            self.live = False
        else:
            self.live = True

    def repaint(self, screen, position):
        p = super().repaint(screen, position)
        pygame.draw.circle(screen, self.color, p, self.r)

    def update(self):
        if not self.live:
            self.kill()
        elif self.touch():
            self.plus()
            self.kill()
        super().update(lambda:self.master.master.field.touch(self, True))

    def touch(self):
        d = ((self.x-self.player.x)**2 + (self.y-self.player.y)**2)**0.5
        if d < self.r + self.player.r:
            return True
        else:
            return False


class Heart(Stuff):
    def __init__(self, master):
        super().__init__(master)
        self.color = [255, 0, 0]

    def plus(self):
        self.player.addBlood()

    def kill(self):
        try:
            self.master.hearts.remove(self)
            self.master.update_live()
        except ValueError:
            pass


class Star(Stuff):
    def __init__(self, master):
        super().__init__(master)
        self.color = [0, 255, 255]

    def plus(self):
        self.player.score += 1

    def kill(self):
        try:
            self.master.stars.remove(self)
            self.master.update_live()
        except ValueError:
            pass

