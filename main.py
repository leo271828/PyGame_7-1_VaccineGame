# -*- coding: utf-8 -*-
import time
import pygame
from pygame.locals import *
from setting import *
import sys
import os  # 增

from player import Player
import wall
import monster
import stuff

setting = [wh, bg, speed, distance, field_wh]
# bg = setting[1]
wh = setting[0]  # [width, height]
background_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "bg_chiheisen_green1.jpg")),
                                          (800, 600))  # 增
FPS = 30


class Main:
    '''負責掌控主程序'''

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(wh)
        pygame.display.set_caption('疫情求生')

        # house blood
        self.house = pygame.transform.scale(pygame.image.load(os.path.join("images", "house.png")), (60, 60))
        self.vaccine_coverage = pygame.transform.scale(
            pygame.image.load(os.path.join("images", "vaccine_coverage.png")), (60, 60))

        # 物件初始化
        self.clock = pygame.time.Clock()

    def repaint(self, screen):
        '''將各個物件顯示到螢幕上。position為視野的座標，將此變數傳到各個物件，使物件在相對於座標的地方進行繪圖。repaint繼承自GameObject'''
        position = (self.player.x, self.player.y)
        screen.blit(background_image, (0, 0))  # 增
        self.monster.repaint(screen, position)
        self.field.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)

        # text_2 也就是 house blood ， 移過來這裡
        font = pygame.font.Font('data/freesansbold.ttf', 30)
        text_2 = font.render(' : {0}%'.format(self.field.house.heart), True, [255, 255, 255])
        screen.blit(self.house, (20, 110))
        screen.blit(text_2, (90, 130))

        text_3 = font.render(' : {0}%'.format(100 * (self.field.house.total / self.field.house.people)), True,
                             [255, 255, 255])
        screen.blit(self.vaccine_coverage, (20, 170))
        screen.blit(text_3, (90, 190))

        pygame.display.flip()
        pygame.display.update()

    def update(self):
        '''物件更新'''
        # monster還未完成所以未加進來
        self.player.update()
        self.monster.update()
        self.field.update()
        self.stuff.update()
        # 升級機制

    def gameover(self, screen):
        '''結束畫面'''
        # monster還未完成所以未加進來
        screen.blit(background_image, (0, 0))  # 增
        position = (self.player.x, self.player.y)
        self.field.repaint(screen, position)
        self.monster.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)
        f = pygame.font.Font('data/freesansbold.ttf', 70)
        f2 = pygame.font.Font('data/freesansbold.ttf', 50)
        text1 = f.render('Game Over', True, [255, 255, 0])
        text2 = f2.render('Vaccine coverage: {} %'.format(self.player.sumvaccine), True, self.player.color)
        rect1 = text1.get_rect()
        rect2 = text2.get_rect()
        rect1.center = [wh[0] / 2, wh[1] / 2 - 150]
        rect2.center = [wh[0] / 2, wh[1] / 2 - 50]
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)

        pygame.display.flip()
        pygame.display.update()

    def reset(self):
        # monster還未完成所以未加進來
        self.field = wall.Field(self)
        self.player = Player(self)
        # 怪物
        self.monster = monster.MonsterManager(self)
        self.stuff = stuff.StuffManager(self)
        # 升級機制

    def begin(self):
        '''主程序'''
        play = True  # 設定遊戲狀態
        done = False
        timeup = False
        timelimit = 180  # sec
        t0 = time.time()
        house_time = 0
        self.reset()
        pygame.mixer.init()
        # 音檔
        while not done:
            self.clock.tick(FPS)
            # 這裡 e 我改成 event 因為這樣比較屌
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                # 按下滑鼠攻擊
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player.shut()

            # 判定存活與否，欸乾這裡幹嘛分成三個狀況? 不就死或沒死嗎?
            if not play:
                self.gameover(self.screen)
            elif self.player.blood <= 0 or timeup:
                play = False
            else:
                self.update()
                self.repaint(self.screen)

            # 到計時的部分
            if not timeup and self.player.blood > 0:
                f = pygame.font.SysFont('Comic Sans MS', 20)
                t1 = time.time()
                clock = t1 - t0
                if clock >= timelimit:
                    timeup = True
                else:
                    minute = int((timelimit - clock) // 60)
                    second = (timelimit - clock) % 60
                    second = '%02d' % second
                # print(minute, second)
                self.timer(f, minute, second)

            # house blood 的部分
            # 算法為：每過 6s 扣血 2%
            house_time += 1
            if house_time % (FPS * 6) == 0:
                #print('yoyo')
                self.field.house.heart -= 2

    # time label
    def timer(self, f, minute, second, time_rect_size=60):
        # w, h = setting[0]
        pygame.draw.rect(self.screen, (0, 0, 0, 0), (0, wh[0] - f.get_height(), time_rect_size, 80))
        text_time = f.render(str(minute) + ':' + str(second), True, [255, 255, 255])
        # print(minute, second)
        self.screen.blit(text_time, ((time_rect_size - f.get_linesize() * 1.38) / 2, wh[1] - f.get_height()))
        pygame.display.update()


root = Main()
root.begin()
