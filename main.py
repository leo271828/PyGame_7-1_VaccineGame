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

mute_btn = pygame.transform.scale(pygame.image.load(os.path.join("images", "muse.png")),(80,80)) #音檔
sound_btn  = pygame.transform.scale(pygame.image.load(os.path.join("images", "sound.png")),(80,80)) #音檔


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
        #按鈕
        self.sound_btn = sound_btn
        self.mute_btn  = mute_btn
        self.mute_rect = pygame.Rect(720,100,80,80)
        self.sound_rect = pygame.Rect(640,100,80,80)

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

        #音檔
        screen.blit(self.mute_btn,(720,100))
        screen.blit(self.sound_btn, (640,100))


        pygame.display.flip()
        pygame.display.update()

    def update(self):
        '''物件更新'''
        self.player.update()
        self.monster.update()
        self.field.update()
        self.stuff.update()


    def gameover(self, screen, play):
        '''結束畫面'''
        if play == 1:
            return
        f = pygame.font.Font('data/freesansbold.ttf', 70)
        f2 = pygame.font.Font('data/freesansbold.ttf', 50)
        f3 = pygame.font.Font('data/freesansbold.ttf', 30)

        if play == 0:
            text1 = f.render('Game Over', True, [255, 255, 0])
            text2 = f2.render('Vaccine coverage: {} %' .format(self.field.house.total ), True, self.player.color)
            text3 = f3.render('Enter to restart', True, [128,138,135])

        else :
            text1 = f.render('You Win', True, [255, 255, 0])
            text2 = f2.render('Vaccine coverage: 100 %', True, self.player.color)
            text3 = f3.render('Enter to restart', True, [128,138,135])

        screen.blit(background_image,(0,0)) # 增
        position = (self.player.x, self.player.y)
        self.field.repaint(screen, position)
        self.monster.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)

        rect1 = text1.get_rect()
        rect2 = text2.get_rect()
        rect3 = text3.get_rect()
        rect1.center = [wh[0] / 2, wh[1] / 2 - 150]
        rect2.center = [wh[0] / 2, wh[1] / 2 - 50]
        rect3.center = [wh[0] / 2 +250, wh[1] / 2 +250]
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)
        screen.blit(text3, rect3)

        pygame.display.flip()
        pygame.display.update()
        self.again()
        
    def again(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    root.begin()
    
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
        play = 1     #設定遊戲狀態
        self.done = False
        timeup = False
        timelimit = 180  # sec
        t0 = time.time()
        house_time = 0
        self.reset()
        pygame.mixer.init()

        # 音檔
        background_sound = pygame.mixer.Sound('data/sound/background.mp3')
        background_sound.set_volume(0.2)
        background_sound.play(-1)
        self.shoot_sound = pygame.mixer.Sound('data/sound/shoot.mp3')
        self.shoot_sound.set_volume(0.2)

        while not self.done:
            self.clock.tick(FPS)
            x, y = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                # 按下滑鼠攻擊
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.mute_rect.collidepoint(x,y):
                        #音檔
                        background_sound.stop()
                        self.shoot_sound.set_volume(0)
                    if self.sound_rect.collidepoint(x,y):
                        #音檔
                        background_sound.play()
                        self.shoot_sound.set_volume(0.2)
                    else:
                        self.player.shut()
                        # 音檔
                        self.shoot_sound.play()

            if play == 0:
                self.gameover(self.screen,play)
                background_sound.stop()
            elif play == 2:
                self.gameover(self.screen,play)
                background_sound.stop()
            elif self.player.blood <= 0 or self.field.house.heart <= 0 or timeup:
                play = 0
                # 音檔
                lose_sound = pygame.mixer.Sound('data/sound/lose.wav')
                lose_sound.set_volume(0.2)
                lose_sound.play()
            elif self.field.house.total >= 100:
                play = 2
                # 音檔
                win_sound = pygame.mixer.Sound('data/sound/win.mp3')
                win_sound.set_volume(0.2)
                win_sound.play()
            else:
                self.update()
                self.repaint(self.screen)
            
            # 到數計時的部分
            if (not timeup and self.player.blood > 0) and (play == 1) :
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
