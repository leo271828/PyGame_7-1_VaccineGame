import pygame
from pygame.locals import *
from setting import *
import math
import os

from game_object import GameObject
from bullet import PlayerBullet
from wall   import House


wh = GameObject.setting[0]
speed = GameObject.setting[2]
distance = GameObject.setting[3]

# touchSound = pygame.mixer.Sound('data/sound/scream.wav')
# touchSound.set_volume(0.2)
# upSound = pygame.mixer.Sound('data/sound/fairydust.wav')
# upSound.set_volume(1)
# 換入圖片
Player_image = pygame.image.load(os.path.join("images", "animalface_neko.png"))
Alcohol_image = pygame.image.load(os.path.join("images", "alcohol.png"))
Mask_image = pygame.image.load(os.path.join("images", "mask.png"))
Vaccine_image = pygame.image.load(os.path.join("images", "vaccine.png"))
House_image   = pygame.image.load(os.path.join("images", "house.png"))
coverage_image = pygame.image.load(os.path.join("images", "vaccine_coverage.png"))
class Player(GameObject):
    '''玩家物件，可以上下左右移動'''

    def __init__(self, master):
        super().__init__(master)
        # 位置、狀態
        self.x = -200
        self.y = 100
        self.r = 30
        self.angle = 0
        self.v = [0, 0]
        # 外型
        self.color = [50, 120, 255]
        # 配件
        self.gun = PlayerGun_alcohol(self)
        self.Player_alcohol = PlayerGun_alcohol(self)
        self.Player_mask = PlayerGun_mask(self)
        self.House = House(self)
        # 槍的切換
        self.gun_change = 1

        self.bullet = []
        self.shuting = False
        self.level_factor = [0, 9]
        self.level = 0
        # 遊戲屬性
        self.power = 1
        self.cooldown = 0
        self.last_shut = 0
        self.CD = 500
        self.speed = 2
        self.blood = 5
        self.HP = 5
        self.DEF = 0
        # 獲得疫苗總數
        self.sumvaccine = 0

        # 圖片

        self.player = pygame.transform.scale(Player_image, (60, 60))
        self.vaccine = pygame.transform.scale(Vaccine_image, (40, 80))
        self.house = pygame.transform.scale(House_image, (60, 60))
        self.vaccine_coverage = pygame.transform.scale(coverage_image, (60, 60))

    def addvaccine(self, vaccine):
        self.sumvaccine += vaccine

    def repaint(self, screen, position):
        '''
        在此實做player的座標轉換是為了未來的鏡頭移動所準備，在實做此功能後，未來可維護性較高
        '''
        x, y = super().repaint(screen, position)
        screen.blit(self.player, (x - 30, y - 30))

        self.gun.repaint(screen, position)
        for b in self.bullet:
            b.repaint(screen, position, self.gun_change)

        # 獲得疫苗數
        font = pygame.font.Font('data/freesansbold.ttf', 30)
        text_1 = font.render(': %s' % self.sumvaccine, True, [255, 255, 255])
        screen.blit(self.vaccine, (30, 30))
        screen.blit(text_1, (90, 50))
        text_2  = font.render(':{0}%' .format(self.House.heart), True, [255, 255, 255])
        screen.blit(self.house, (20, 110))
        screen.blit(text_2, (90, 130))

        text_3 = font.render(':{0}%' .format(self.House.total/self.House.people), True, [255, 255, 255])
        screen.blit(self.vaccine_coverage, (20, 170))
        screen.blit(text_3, (90, 190))

        b = -1
        # 繪製血量
        for b in range(int(self.blood)):
            pygame.draw.rect(screen, [255, 0, 0], (x - 70 + 14 * b, y - 90, 10, 10))
        b += 1
        w = max(self.map(0, 1, 0, 10, (self.blood - int(self.blood))), 0)
        if w:
            pygame.draw.rect(screen, [255, 0, 0], (x - 70 + 14 * b, y - 90, w, 10))

    def update(self):
        '''更新狀態'''
        # 如果碰到殭屍、狙擊手、敵方子彈
        zombie = self.master.monster.touch(self, True)
        if self.delay(500) and zombie:
            self.hit(zombie)
            # 向反方向反彈
        # 更新玩家子彈
        for b in self.bullet:
            b.update()

        # 如果按下按鍵就移動
        if self.iskey(K_w):
            self.v[1] += -self.speed
        if self.iskey(K_s):
            self.v[1] += self.speed
        if self.iskey(K_d):
            self.v[0] += self.speed
        if self.iskey(K_a):
            self.v[0] += -self.speed
        if self.iskey(K_f):
            if self.gun_change == 1:
                self.gun = self.Player_mask
                self.gun_change = 2
            else:
                self.gun = self.Player_alcohol
                self.gun_change = 1

        super().update(lambda: self.master.field.touch(self))
        now = pygame.time.get_ticks()
        self.cooldown = self.map(0, self.CD, 0, 1, min(now - self.last_shut, self.CD))

        # 如果正在發射狀態就執行
        if self.shuting:
            self.shut()
        self.gun.update()

    def shut(self):
        # 沒有在發射中，代表是第一次執行
        if not self.shuting:
            self.shuting = True
            self.gun.shuting = True
        # 按鍵放開，結束發射模式
        elif not self.iskey(K_SPACE):
            self.bullet.append(PlayerBullet(self, power=self.power * self.cooldown))
            self.move(self.gun.angle, -6)
            self.shuting = False
            self.last_shut = pygame.time.get_ticks()

    def hit(self, person):
        self.last_time = pygame.time.get_ticks()
        self.blood -= max(person.power - self.DEF, 0)
        self.near((person.x, person.y), -30)
        if person in self.master.monster.bullet:
            person.kill()
        # touchSound.play()
        print(self.blood)

    def addBlood(self):
        self.blood = min(self.blood + 1, self.HP)

    def get(self):
        return self.gun_change


class Gun(GameObject):
    def __init__(self, master):
        super().__init__(master)
        self.x = self.master.x
        self.y = self.master.y
        self.turn = speed
        self.angle = 0
        self.shuting = False
        self.last_time = 0

    def Sniper_repaint(self, screen, position):
        x, y = super().repaint(screen, position)
        point = [(0, -90), (10, -70), (-10, -70)]
        angle = self.angle + self.master.angle
        newpoint = []
        for px, py in point:
            nx = px * math.cos(angle + math.pi / 2) - py * math.sin(angle + math.pi / 2) + x
            ny = px * math.cos(angle) - py * math.sin(angle) + y
            newpoint.append((nx, ny))
        color = [c * self.master.cooldown for c in self.master.color] if type(
            self.master).__name__ == 'Player' else self.master.color
        pygame.draw.polygon(screen, color, newpoint)

    def Player_repaint(self, screen, position):
        x, y = super().repaint(screen, position)
        px = 0
        py = -80
        angle = self.angle + self.master.angle
        nx = px * math.cos(angle + math.pi / 2) - py * math.sin(angle + math.pi / 2) + x - 25
        ny = px * math.cos(angle) - py * math.sin(angle) + y - 25
        screen.blit(self.image, (nx, ny))

    def update(self):
        self.x = self.master.x
        self.y = self.master.y
        self.angle += self.turn

        if self.shuting:
            self.shut()

    def shut(self):
        # 如果第一次按下
        if self.last_time == 0:
            self.turn *= -0.25
            self.last_time = pygame.time.get_ticks()
        # 如果超過一秒，換方向
        elif pygame.time.get_ticks() - self.last_time > 500:
            self.turn *= -1
            self.last_time = pygame.time.get_ticks()
        # 如果按鍵已放開
        elif not self.master.shuting:
            self.shuting = False
            self.turn *= 4
            self.last_time = 0


# 敵人的槍
class SniperGun(Gun):
    def __init__(self, master) -> None:
        super().__init__(master)

    def repaint(self, screen, position):
        super().Sniper_repaint(screen, position)


# 玩家的槍
class PlayerGun_alcohol(Gun):
    def __init__(self, master):
        super().__init__(master)
        self.alcohol = pygame.transform.scale(Alcohol_image, (50, 50))
        self.image = self.alcohol

    def repaint(self, screen, position):
        super().Player_repaint(screen, position)
        self.image = self.alcohol

    def update(self):
        self.x, self.y = self.master.x, self.master.y
        # 計算滑鼠相對於中心的角度
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - wh[0] / 2
        dy = mouse_y - wh[1] / 2
        self.angle = math.atan2(dy, dx)

        if self.shuting:
            self.shut()


class PlayerGun_mask(Gun):
    def __init__(self, master):
        super().__init__(master)
        self.mask = pygame.transform.scale(Mask_image, (50, 50))
        self.image = self.mask

    def repaint(self, screen, position):
        super().Player_repaint(screen, position)
        self.image = self.mask

    def update(self):
        self.x, self.y = self.master.x, self.master.y
        # 計算滑鼠相對於中心的角度
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - wh[0] / 2
        dy = mouse_y - wh[1] / 2
        self.angle = math.atan2(dy, dx)

        if self.shuting:
            self.shut()
