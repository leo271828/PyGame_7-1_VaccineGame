import pygame
from pygame.locals import *

from game_object import *

wh = setting['wh']
cardName = ["HP",
            "ATK",
            "CD",
            "DEF"
]

class Card(GameObject):
    def __init__(self, master, name, p=0):
        self.master = master
        self.name = name
        self.player = master.player
        self.x = wh[0]/6*(p+2)
        self.y = wh[1]/4*3

    def repaint(self, screen, position):
        rect = [0, 0, 150, 150]
        rect = pygame.rect.Rect(rect)
        rect.center = (self.x, self.y)
        pygame.draw.rect(screen, [200, 200, 200], rect)
        font = pygame.font.Font('data/freesansbold.ttf', 30)
        text = font.render(self.name, True, [0, 0, 0])
        rect = text.get_rect()
        rect.center = (self.x, self.y)
        screen.blit(text, rect)

    def run(self):
        if self.name == "HP":
            self.player.HP += 1
            self.player.blood += 1
        elif self.name == "ATK":
            self.player.power += 0.5
        elif self.name == "CD":
            self.player.CD -= 50 if self.player.CD > 200 else 0
        elif self.name == "DEF":
            self.player.DEF += 0.1 if self.player.DEF <= 0.6 else 0
        elif self.name == "NONE":
            pass
        print(self.name)

class CardManager(Manager):
    def level_up(self):
        self.live = []
        cards = cardName.copy()
        for c in range(2):
            name = random.choice(cards)
            self.live.append(Card(self, name, c))
            cards.remove(name)
        self.live.append(Card(self, "NONE", 2))
        self.last_time = 1

    def update(self):
        if self.last_time:
            mode = True
            if self.iskey(K_j):
                self.live[0].run()
            elif self.iskey(K_k):
                self.live[1].run()
            elif self.iskey(K_l):
                self.live[2].run()
            else:
                mode = False
            if mode:
                self.live = []
                self.last_time = 0

