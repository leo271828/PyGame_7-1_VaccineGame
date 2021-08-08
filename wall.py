import pygame
from pygame.locals import *
from pygame import Rect

from game_object import GameObject

w = 80
h = 600
g = 250

class Wall(GameObject):
    def __init__(self, master, position):
        super().__init__(master)
        self.x, self.y = position
        self.color = [200, 200, 200]
        self.rects = [Rect(self.x - w/2, self.y - h/2, w, h),
                      Rect(self.x - h/2, self.y - w/2, h, w)]
    
    def update(self):
        pass
    
    def repaint(self, screen, position):
        x, y = super().repaint(screen, position)
        pygame.draw.rect(screen, self.color, (x - w/2, y - h/2, w, h))
        pygame.draw.rect(screen, self.color, (x - h/2, y - w/2, h, w))

    def touch(self, person):
        for r in self.rects:
            x = min(r.x+r.w, person.x)
            x = max(r.x, x)
            y = min(r.y+r.h, person.y)
            y = max(r.y, y)
            distance = ((person.x - x)**2 + (person.y - y)**2) ** 0.5
            if distance < person.r:
                return True
        else:
            return False

        
class Field(GameObject):
    def __init__(self, master):
        super().__init__(master)
        self.color = [255, 255, 255]
        self.w, self.h = self.setting['field_wh']
        self.edge = [Rect(-self.w, -self.h, 2*self.w, 100),
                     Rect(-self.w, -self.h, 100, 2*self.h),
                     Rect(-self.w, self.h-100, 2*self.w, 100),
                     Rect(self.w-100, -self.h, 100, 2*self.h)]
        self.walls = []
        mid = (0, 0)
        for i in range(-self.w + 2*h, self.w - 2*h, 2*h + g):
            for j in range(-self.h + 2*h, self.h - 2*h, 2*h + g):
                mid = (i, j)
                self.add_wall(mid)
        self.live_walls = []
        self.last_time = 0
    
    def repaint(self, screen, position):
        x, y = super().repaint(screen, position)
        for e in self.edge:
            paint_e = e.copy()
            paint_e.x += x
            paint_e.y += y
            pygame.draw.rect(screen, self.color, paint_e)
        for wall in self.live_walls:
            wall.repaint(screen, position)
    
    def add_wall(self, mid):
        a = (w + g) / 2
        b = (w + g + h) / 2
        self.walls.append(Wall(self, (mid[0] + a,mid[1] + b)))
        self.walls.append(Wall(self, (mid[0] - b,mid[1] + a)))
        self.walls.append(Wall(self, (mid[0] - a,mid[1] - b)))
        self.walls.append(Wall(self, (mid[0] + b,mid[1] - a)))

    def update(self):
        if pygame.time.get_ticks() - self.last_time > 500:
            p = self.master.player
            self.live_walls = [w for w in self.walls if abs(w.x-p.x) < 1500 and abs(w.y-p.y) < 1500 ]
            self.last_time = pygame.time.get_ticks()

    def touch(self, person, a=False):
        array = self.walls if a  else self.live_walls
        for w in self.live_walls:
            if w.touch(person):
                return True
        for r in self.edge:
            x = min(r.x+r.w, person.x)
            x = max(r.x, x)
            y = min(r.y+r.h, person.y)
            y = max(r.y, y)
            distance = ((person.x - x)**2 + (person.y - y)**2) ** 0.5
            if distance < person.r:
                return True
        else:
             return False

