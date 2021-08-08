import pygame
from pygame.locals import *
from setting import *
import math
import os


from game_object import GameObject
from bullet import PlayerBullet


wh = GameObject.setting[0]
speed = GameObject.setting[2]
distance = GameObject.setting[3]

# touchSound = pygame.mixer.Sound('data/sound/scream.wav')
# touchSound.set_volume(0.2)
# upSound = pygame.mixer.Sound('data/sound/fairydust.wav')
# upSound.set_volume(1)
#換入圖片
Player_image = pygame.image.load(os.path.join("images", "animalface_neko.png"))



class Player(GameObject):
    '''玩家物件，可以上下左右移動'''
    def __init__(self, master):
        super().__init__(master)
        #位置、狀態
        self.x = -200
        self.y = 100
        self.r = 30
        self.angle = 0
        self.v = [0, 0]
        #外型
        self.color = [50, 200, 200]
        self.sound = pygame.mixer.Sound('data/sound/scream.wav')
        self.sound.set_volume(0.2)
        #配件
        self.gun = PlayerGun(self)
        self.bullet = []
        self.shuting = False
        self.level_factor = [0, 9]
        self.level = 0
        self.next_score = self.next()
        #遊戲屬性
        self.power = 1
        self.cooldown = 0
        self.last_shut = 0
        self.CD = 500
        self.score = 0
        self.speed = 2
        self.blood = 5
        self.HP = 5
        self.DEF = 0
        
        #圖片
        
        self.player = pygame.transform.scale(Player_image, (50, 50))
        
    def next(self):
        d = 5
        an = 10
        s = an
        while True:
            an += d
            s += an
            yield s

    def repaint(self, screen, position):
        '''
        在此實做player的座標轉換是為了未來的鏡頭移動所準備，在實做此功能後，未來可維護性較高
        '''
        x, y = super().repaint(screen, position)
        screen.blit(self.player, (x-25,y-25))
        #pygame.draw.circle(screen, self.color, (x, y), self.r, 5)
        self.gun.repaint(screen, position)
        for b in self.bullet:
            b.repaint(screen, position)

        score = self.map(self.level_factor[-2], self.level_factor[-1], 0, 1000, self.score)
        score_block = Rect(170, 50, score, 30)
        pygame.draw.rect(screen, [0, 255, 255], score_block)
        b = -1
        for b in range(int(self.blood)):
            pygame.draw.rect(screen, [255,0,0], (x-70+14*b, y-90, 10, 10))
        b += 1
        w = max(self.map(0, 1, 0, 10, (self.blood - int(self.blood))), 0)
        if w:
            pygame.draw.rect(screen, [255, 0, 0], (x-70+14*b, y-90, w, 10))

        font = pygame.font.Font('data/freesansbold.ttf', 30)
        text = font.render('level: %s' % self.level, True, [255, 255, 255])
        screen.blit(text, (50,50))

    def update(self):
        '''更新狀態'''
        #如果分數超過最高就升等
        if self.score > self.level_factor[-1]:
            self.level_up()
        zombie = self.master.monster.touch(self, True)
        #如果碰到殭屍、狙擊手、敵方子彈
        if self.delay(500) and zombie:
            self.hit(zombie)
            #向反方向反彈
        #更新玩家子彈
        for b in self.bullet:
            b.update()
        
        #如果按下按鍵就移動
        if self.iskey(K_w):
            self.v[1] += -self.speed
        if self.iskey(K_s):
            self.v[1] += self.speed
        if self.iskey(K_d):
            self.v[0] += self.speed
        if self.iskey(K_a):
            self.v[0] += -self.speed
        super().update(lambda :self.master.field.touch(self))
        now = pygame.time.get_ticks()
        self.cooldown = self.map(0, self.CD, 0, 1, min(now - self.last_shut, self.CD))
        
        #如果正在發射狀態就執行
        if self.shuting:
            self.shut()
        self.gun.update()
        
    def shut(self):
        #沒有在發射中，代表是第一次執行
        if not self.shuting:
            self.shuting = True
            self.gun.shuting = True
        #按鍵放開，結束發射模式
        elif not self.iskey(K_SPACE):
            self.bullet.append(PlayerBullet(self, power=self.power * self.cooldown))
            self.move(self.gun.angle, -6)
            self.shuting = False
            self.last_shut = pygame.time.get_ticks()

    def addPoint(self, score):
        self.score += score

    def hit(self, person):
        self.last_time = pygame.time.get_ticks()
        self.blood -= max(person.power-self.DEF, 0)
        self.near((person.x, person.y), -30)
        if person in self.master.monster.bullet:
            person.kill()
        # touchSound.play()
        print(self.blood)

    def addBlood(self):
        self.blood = min(self.blood+1, self.HP)

    def level_up(self):
        self.level += 1
        self.level_factor.append(next(self.next_score))
        self.master.card.level_up()
        # upSound.play()


class Gun(GameObject):
    def __init__(self, master):
        super().__init__(master)
        self.x = self.master.x
        self.y = self.master.y
        self.turn = speed
        self.angle = 0
        self.shuting = False
        self.last_time = 0

    def repaint(self, screen, position):
        x, y = super().repaint(screen, position)
        point = [(0, -90), (10, -70), (-10, -70)]
        angle = self.angle + self.master.angle
        newpoint = []
        for px, py in point:
            nx = px * math.cos(angle + math.pi / 2) - py * math.sin(angle + math.pi / 2) + x
            ny = px * math.cos(angle) - py * math.sin(angle) + y
            newpoint.append((nx, ny))
        color = [c * self.master.cooldown for c in self.master.color] if type(self.master).__name__ == 'Player' else self.master.color
        pygame.draw.polygon(screen, color, newpoint)

    def update(self):
        self.x = self.master.x
        self.y = self.master.y
        self.angle += self.turn

        if self.shuting:
            self.shut()

    def shut(self):
        #如果第一次按下
        if self.last_time == 0:
            self.turn *= -0.25
            self.last_time = pygame.time.get_ticks()
        #如果超過一秒，換方向
        elif pygame.time.get_ticks() - self.last_time > 500:
            self.turn *= -1
            self.last_time = pygame.time.get_ticks()
        #如果按鍵已放開
        elif not self.master.shuting:
            self.shuting = False
            self.turn *= 4
            self.last_time = 0
# 敵人的槍
class SniperGun(Gun):
    def __init__(self, master) -> None:
        super().__init__(master)

# 玩家的槍
class PlayerGun(Gun):
    def __init__(self, master):
        super().__init__(master)
    
    def update(self):
        self.x, self.y = self.master.x, self.master.y
        # 計算滑鼠相對於中心的角度
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - wh[0]/2
        dy = mouse_y - wh[1]/2
        self.angle = math.atan2(dy, dx)
        
        if self.shuting:
            self.shut()
