#-*- coding: utf-8 -*-
import time
import pygame
from pygame.locals import *
from setting import *
import sys
import os #增

from player import Player
import wall
import monster
import stuff

screen = pygame.display.set_mode(wh)#增
setting = [wh, bg, speed, distance, field_wh]
#bg = setting[1]     
wh = setting[0]     # [width, height]
background_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "bg_chiheisen_green1.jpg")),(800,600)) #增
intro_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "intro.png")),(800,600)) #增加超棒的遊戲說明圖片
intro_move = pygame.transform.scale(pygame.image.load(os.path.join("images", "intro_move.png")),(800,600)) 
intro_attack = pygame.transform.scale(pygame.image.load(os.path.join("images", "intro_attack.png")),(800,600)) 
intro_home = pygame.transform.scale(pygame.image.load(os.path.join("images", "intro_home.png")),(800,600)) 
intro_list = [intro_home,intro_attack,intro_move,intro_image]

FPS  =30

class Main:
    '''負責掌控主程序'''
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(wh)
        pygame.display.set_caption('疫情求生')

        # house blood
        self.vaccine = pygame.transform.scale(pygame.image.load(os.path.join("images", "vaccine_coverage.png")), (60, 60))
        self.house = pygame.transform.scale(pygame.image.load(os.path.join("images", "house.png")), (60, 60))


        #物件初始化
        self.clock = pygame.time.Clock()

    def repaint(self, screen):
        '''將各個物件顯示到螢幕上。position為視野的座標，將此變數傳到各個物件，使物件在相對於座標的地方進行繪圖。repaint繼承自GameObject'''
        position = (self.player.x, self.player.y)
        screen.blit(background_image,(0,0)) #增
        self.monster.repaint(screen, position)
        self.field.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)

        # 畫面左上角的疫苗資訊
        font = pygame.font.Font('data/freesansbold.ttf', 30)
        text_1 = font.render(': %s' % self.player.sumvaccine, True, [255, 255, 255])
        screen.blit(self.vaccine, (20, 30))
        screen.blit(text_1, (90, 50))

        text_2  = font.render(' : {0}%' .format(int(round(self.field.house.heart, 0))), True, [255, 255, 255])
        screen.blit(self.house, (20, 110))
        screen.blit(text_2, (90, 130))



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
        screen.blit(background_image,(0,0)) #增
        position = (self.player.x, self.player.y)
        self.field.repaint(screen, position)
        self.monster.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)
        f = pygame.font.Font('data/freesansbold.ttf', 70)
        f2 = pygame.font.Font('data/freesansbold.ttf', 50)
        text1 = f.render('Game Over', True, [255, 255, 0])
        text2 = f2.render('Vaccine coverage: {} %' .format(self.field.house.total), True, self.player.color)
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
        #怪物
        self.monster = monster.MonsterManager(self)
        self.stuff = stuff.StuffManager(self)
        # 升級機制

    def begin(self):
        '''主程序'''
        play = True     #設定遊戲狀態
        done = False
        timeup = False
        timelimit = 180  # sec
        t0 = time.time()
        house_time = 0
        self.reset()
        pygame.mixer.init()
        #音檔
        while not done:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                # 按下滑鼠攻擊
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player.shut()

            # 判定存活與否，欸乾這裡幹嘛分成三個狀況? 不就死或沒死嗎?
            if not play:
                self.gameover(self.screen)
            elif self.player.blood <= 0 or self.field.house.heart <=0 or timeup:
                play = False
            else:
                self.update()
                self.repaint(self.screen)
                
            # 到數計時的部分
            if not timeup and self.player.blood > 0:
                f = pygame.font.SysFont('Comic Sans MS', 50)
                t1 = time.time()
                clock = t1 - t0
                if clock >= timelimit:
                    timeup = True
                else:
                    minute = int((timelimit-clock) // 60)
                    second = (timelimit-clock) % 60
                    second = '%02d' % second
                # print(minute, second)
                self.timer(f, minute, second)
            
            # house blood 的部分
            # 算法為：每過 6s 扣血 2%
            # 修　　：每過 1s 扣血 10/12% ，代表 120s 後會死亡
            house_time += 1
            if house_time % FPS == 0 :
                self.field.house.heart -= (10/12)
            if house_time % (FPS*30) == 0 :
                self.player.level += 10
            # 還一次疫苗就 +2%
            if self.player.temp != 0 :
                self.field.house.heart += self.player.temp
                if self.field.house.heart > 100 :
                    self.field.house.heart = 100
                self.player.temp = 0
                
            
    # time label
    def timer(self, f, minute, second, time_rect_size=100):
        #w, h = setting[0]
        pygame.draw.rect(self.screen, (0, 0, 0, 0), (0, wh[0] - f.get_height(), time_rect_size, 100))
        text_time = f.render(str(minute) + ':' + str(second), True, [255, 255, 255])
        #print(minute, second)
        self.screen.blit(text_time, ((wh[0]-time_rect_size-20,0)))
        pygame.display.update()

    def intro(self):
        i = 0
        done = True
        image = intro_list.pop()
        while done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        i += 1
                        if i <= 3:
                            image = intro_list.pop()
                        else:
                            self.in_intro = False
                            done = False

                screen.blit(image,(0,0))    
                pygame.display.update()

root = Main()
root.intro()
if not root.in_intro:
    root.begin()
