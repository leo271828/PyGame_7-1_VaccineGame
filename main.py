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

setting = [wh, bg, speed, distance, field_wh]
bg = setting[1]
wh = setting[0]
background_image = pygame.transform.scale(pygame.image.load(os.path.join("images", "bg_chiheisen_green1.jpg")),(800,600)) #增

class Main:
    '''負責掌控主程序'''
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(wh)
        pygame.display.set_caption('疫情求生')

        #物件初始化
        self.clock = pygame.time.Clock()

    def repaint(self, screen):
        '''將各個物件顯示到螢幕上。position為視野的座標，將此變數傳到各個物件，使物件在相對於座標的地方進行繪圖。repaint繼承自GameObject'''
        # monster還未完成所以未加進來
        position = (self.player.x, self.player.y)
        screen.blit(background_image,(0,0)) #增
        self.monster.repaint(screen, position)
        self.field.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)
        # 升級機制
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

    def gameover(self, screen, tops=[]):
        '''結束畫面'''
        # monster還未完成所以未加進來
        screen.blit(background_image,(0,0)) #增
        position = (self.player.x, self.player.y)
        self.field.repaint(screen, position)
        self.monster.repaint(screen, position)
        self.player.repaint(screen, position)
        self.stuff.repaint(screen, position)
        f = pygame.font.Font('data/freesansbold.ttf', 90)
        text1 = f.render('Game Over', True, [255,255,100])
        text2 = f.render('Score: %s' % self.player.score, True, self.player.color)
        rect1 = text1.get_rect()
        rect2 = text2.get_rect()
        rect1.center = [wh[0]/2, wh[1]/2 - 300]
        rect2.center = [wh[0]/2, wh[1]/2 - 150]
        screen.blit(text1, rect1)
        screen.blit(text2, rect2)

        f = pygame.font.Font('data/freesansbold.ttf', 50)
        for i in range(len(tops)):
            color = self.player.color if int(tops[i]) == self.player.score else [255,255,255]
            text = f.render('%s: %s' % (i+1, tops[i]), True, color)
            screen.blit(text, (wh[0]/2-100, wh[1]/2 + 50*(i-1)))

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
        timelimit = 10  # sec
        t0 = time.time()
        self.reset()
        pygame.mixer.init()
        #音檔
        while not done:
            # 這裡 e 我改成 event 因為這樣比較屌
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                # 按下滑鼠攻擊
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player.shut()
                # 這裡原本有 e.type == pygame.KEYDOWN 那一塊 我全部刪掉了 所以這行你可以槓掉
            # 判定存活與否
            if not play:
                self.gameover(self.screen, tops)
            elif self.player.blood <= 0 or timeup:
                play = False
                #音檔
                tops = self.top(self.player.score)
                #音檔
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
                    minute = int((timelimit-clock) // 60)
                    second = (timelimit-clock) % 60
                    second = '%02d' % second
                # print(minute, second)
                self.timer(f, minute, second)
                
            self.clock.tick(30)
            
    # time label
    def timer(self, f, minute, second, time_rect_size=60):
        w, h = setting[0]
        pygame.draw.rect(self.screen, (0, 0, 0, 0), (0, w - f.get_height(), time_rect_size, 80))
        text_time = f.render(str(minute) + ':' + str(second), True, [255, 255, 255])
        #print(minute, second)
        self.screen.blit(text_time, ((time_rect_size - f.get_linesize() * 1.38) / 2, h - f.get_height()))
        pygame.display.update()
    
    # 其實也不用算排行 下面一坨也可以刪掉
    @staticmethod
    def top(score):
        '''計算排行榜，排序分數，返回前七名並儲存到文件裡'''
        try:
            with open('data/score.txt', 'r') as file:
                data = file.read()
                score_list = data.split('\n')
        except FileNotFoundError:
            score_list = ['0' for i in range(7)]
        for s in range(len(score_list)):
            if score > int(score_list[s]):
                score_list.insert(s, str(score))
                break
        while len(score_list) > 7:
            del score_list[-1]
        with open('data/score.txt', 'w') as file:
            file.write('\n'.join(score_list))
        return score_list

root = Main()
root.begin()
