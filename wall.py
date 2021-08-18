import pygame
import random
import os
from pygame.locals import *
from pygame import Rect
from setting import *

from game_object import GameObject

w = 80
h = 600
g = 250
house_x, house_y = 300, 300
WALL_IMAGE_1 = pygame.transform.scale(pygame.image.load(os.path.join("images", "renga_pattern.png")),(h,w)) #增
WALL_IMAGE_2 = pygame.transform.scale(pygame.image.load(os.path.join("images", "renga_pattern2.png")),(w,h)) #增
house_image = pygame.transform.scale(pygame.image.load('images/house.png'), (house_x, house_y))

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
        screen.blit(WALL_IMAGE_1,(x - h/2, y - w/2))#增
        screen.blit(WALL_IMAGE_2,(x - w/2, y - h/2))#增
        
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
        self.w, self.h = self.setting[4]
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

        # House
        self.house = House(self)
    
    def repaint(self, screen, position):
        x, y = super().repaint(screen, position)
        for e in self.edge:
            paint_e = e.copy()
            paint_e.x += x
            paint_e.y += y
            pygame.draw.rect(screen,[156,168,184], paint_e)
        for wall in self.live_walls:
            wall.repaint(screen, position)

        # House
        self.house.repaint(screen, position)

    
    def add_wall(self, mid):
        a = (w + g) / 2
        b = (w + g + h) / 2
        self.walls.append(Wall(self, (mid[0] + a,mid[1] + b)))
        self.walls.append(Wall(self, (mid[0] - b,mid[1] + a)))
        self.walls.append(Wall(self, (mid[0] - a,mid[1] - b)))
        self.walls.append(Wall(self, (mid[0] + b,mid[1] - a)))

    def update(self):
        # 當貓咪回家時，疫苗歸還
        p = self.master.player
        if self.house.rect.collidepoint(p.x, p.y):
            self.house.total += p.sumvaccine
            p.temp += p.sumvaccine*2 # 還一根疫苗可以 +2%
            p.sumvaccine = 0

        if pygame.time.get_ticks() - self.last_time > 500:
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
            if distance < person.r+30:
                return True
            else:
                return False

class House(GameObject):
    def __init__(self, master):
        super().__init__(master)
        self.image = house_image
        self.total = 0
        self.heart = 100 
        self.people = 100
        # house 的範圍 
        self.rect = pygame.Rect(0, 4700, house_x, house_y)
        self.vaccine_coverage = pygame.transform.scale(pygame.image.load(os.path.join("images", "vaccine_coverage.png")), (60, 60))
        self.loc = [random.randrange(-1, 2, 2), random.randrange(-1, 2, 2)]

    def repaint(self, screen, position):
        # 相對於畫面正中心點的位置 (x, y)
        x, y = super().repaint(screen, position)
        dx, dy = (self.loc[0]*(field_wh[0] - 300) - house_x/2), (self.loc[1]*(field_wh[1] - 300) - house_y/2)
        house_location = [x + dx, y + dy]
        screen.blit(house_image, house_location) 
        self.rect = pygame.Rect(dx, dy, house_x, house_y)

        font = pygame.font.Font('data/freesansbold.ttf', 30)
        if int(100 * (self.total / self.people)) >= 100:
            text_3 = font.render(' : 100%', True, [255, 255, 255])
        else:
            text_3 = font.render(' : {0}%' .format( int(100 * (self.total / self.people))), True, [255, 255, 255])
        screen.blit(self.vaccine_coverage, (x + dx + 100, y + dy - 20))
        screen.blit(text_3, (x + dx + 160, y + dy))
        #print(self.loc)
