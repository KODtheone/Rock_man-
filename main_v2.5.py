'''
log:
2024年9月8日15:02:05  upload to github
'''


import os
import pickle
import random
from copy import deepcopy
from math import sqrt, atan2, cos, sin, pi
import pygame
from pygame.sprite import *

pygame.init()

'''
基础设定:  
单地图大小    D_width, D_height = 1920, 990   太大的话, tile太多, 现在是  33 * 64 的格子
角色大小      self.rect.width = 28  self.rect.height = 36
# 注意左上角开画, 和 左下角作为绘制开始点 , 所以 height需要匹配...
'''

'''
重写 pygame的 Group的 draw函数, 使得当sprite的rect大小和image大小不匹配时, image blit在rect的中心处
ow : overwrite
'''
class Group_ow(Group):
    # def __init__(self):  # 可以不写  2024年9月7日14:51:43
    #     super().__init__()
    def draw(self, surface):
        sprites = self.sprites()
        # rect: <rect(0, 0, 36, 36)>over
        # self.spritedict.update( zip( sprites, surface.blits( (spr.image, spr.rect, ) for spr in sprites), ))
        self.spritedict.update( zip( sprites, surface.blits( (spr.image, (spr.rect[0] + (spr.rect[2] - spr.image.get_width()) // 2, spr.rect[1] + (spr.rect[3] - spr.image.get_height()) // 2, spr.rect[2],spr.rect[3])) for spr in sprites), ))


D_width, D_height = 1920, 990
SCREEN_RECT = pygame.Rect(0,0,1920,990) # 33 * 64
SCREEN_RECT = pygame.Rect(0,0,1000,500) # 33 * 64
SCREEN = pygame.display.set_mode(SCREEN_RECT.size, 16)   # flag = 16 可以拉动大小
SURFACE = pygame.Surface((D_width, D_height))   # 2024年7月22日21:17:19, 把surface分离出来,整体移动, 方便camera
FRAME_PER_SEC = 60  #  2024年6月27日19:53:37, 现在最大370
FRAME_PER_SEC = 30
# FRAME_PER_SEC = 45
# FRAME_PER_SEC = 3
# FRAME_PER_SEC = 99999
TILE = 30       # 则一个屏幕tile数位 1920 // 30 =64, 990//30 = 33,   33 x 64   的地图
BASICFONT = pygame.font.Font('freesansbold.ttf', 90)
BASICFONT1 = pygame.font.Font('freesansbold.ttf', 30)
# preload  img & sound;  invoke dict
dict_img = {}
dict_sound = {}
for img in os.listdir("./misc"):
    if img.split('.')[1] == "png":
        t = pygame.image.load("misc/" + img).convert_alpha()    #  ## 加上 convert 对速度的优化是巨大的!!!
        dict_img[img] = [t , pygame.transform.flip(t, True, False)]
d_run = [[dict_img["walk_1.png"][0], dict_img["walk_2.png"][0], dict_img["walk_3.png"][0] , dict_img["walk_2.png"][0]],
         [ dict_img["walk_1.png"][1], dict_img["walk_2.png"][1], dict_img["walk_3.png"][1] , dict_img["walk_2.png"][1] ]]
# step 不能进循环
# d_run = [[dict_img["step.png"][0], dict_img["walk_1.png"][0], dict_img["walk_2.png"][0], dict_img["walk_3.png"][0] , dict_img["walk_2.png"][0]],
#          [ dict_img["step.png"][1], dict_img["walk_1.png"][1], dict_img["walk_2.png"][1], dict_img["walk_3.png"][1] , dict_img["walk_2.png"][1] ]]
d_climb = [[dict_img["climb_1.png"][0], dict_img["climb_2.png"][0]], [dict_img["climb_1.png"][1], dict_img["climb_2.png"][1]]]
# shoot when running
d_sr = [[dict_img["walk_shoot_1.png"][0], dict_img["walk_shoot_2.png"][0], dict_img["walk_shoot_3.png"][0] , dict_img["walk_shoot_2.png"][0]],
         [ dict_img["walk_shoot_1.png"][1], dict_img["walk_shoot_2.png"][1], dict_img["walk_shoot_3.png"][1] , dict_img["walk_shoot_2.png"][1] ]]
d_cm_sr = d_cm_run = [[dict_img["cm_run1.png"][0], dict_img["cm_run2.png"][0], dict_img["cm_run3.png"][0] , dict_img["cm_run4.png"][0]],
         [dict_img["cm_run1.png"][1], dict_img["cm_run2.png"][1], dict_img["cm_run3.png"][1] , dict_img["cm_run4.png"][1]]]
# 2024年9月7日15:40:51  角色图片预分组
rock_imgs = [dict_img["climb_shoot.png"], d_climb, d_sr, d_run, dict_img["idle_shoot.png"], dict_img["idle.png"], dict_img["shoot_jump.png"], dict_img["jump.png"]]


# pregroup
P = None
group_p1 = Group_ow()
group_p1_bullet = Group_ow()
group_enemy = Group_ow()
group_solid = Group_ow()
# group_trap = Group_ow()    #trap 等价于, solid + enemy, 所以似乎不需要单独判断
group_bg = Group_ow()
group_ladder = Group_ow()
group_gate = Group_ow()
group_item = Group_ow()
group_jpg = Group_ow()  # 最上层图片,区别于bg(底层图片)
# group 表: group_air, group_ladder, group_solid, group_gate, group_item, group_enemy, group_p1, group_p1_bullet,
group_all_list = [group_bg, group_ladder, group_solid, group_gate, group_item, group_enemy, group_p1_bullet, group_p1, group_jpg, ]  #顺序也要注意,不然挡住了图; 或许把enemy和 enemy的bullet分开,就是为了确定哪个图层在更上面
# 增加一个,专门给菜单用的group
# group_menu = Group_ow()  # 2024年9月7日14:52:27, 这里因为位置我修正过, 用的rect不对. 所以不能用group_ow
group_menu = Group()

# 2024年7月25日18:03:57, map部分实现外界pickle储存, 读取
def load_map():
    res = []
    with open('test.pickle','rb') as f:
        while True:
            try:
                m = pickle.load(f)
                res += m,
            except EOFError:
                break
    return res

maps = load_map()

# 函数
# 画地图
# map表: 1: solid 2:trap 3: ladder  4:gate;    1i: 敌人ei      30+ boss, 31, cut man
def create_map(map):
    m,n = len(map), len(map[0])
    for i in range(m):
        for j in range(n):
            #  修改图片从 bottomleft开始画后 坐标上,要变成 (i + 1)
            if map[i][j] == 1:    group_solid.add(Solid(j * TILE, (i + 1) * TILE))
            elif map[i][j] == 2:
                t = Trap(j * TILE, (i + 1) * TILE)
                group_solid.add(t)
                group_enemy.add(t)
            elif map[i][j] == 3:  group_ladder.add(Ladder(j*TILE,(i + 1)*TILE))

            elif map[i][j] == 13:  group_enemy.add(E3(j*TILE,(i + 1)*TILE))
            elif map[i][j] == 14:  group_enemy.add(E4(j*TILE,(i + 1)*TILE))
            elif map[i][j] == 31:  group_enemy.add(Cut_man(j*TILE,(i + 1)*TILE))

# class sprite
class Tile(Sprite):
    def __init__(self, img, resize = None):  #img 直接传入 img object
        super().__init__()
        self.image = img    # self.image 这里的image是必须的 , 因为在 sprite中,
        if resize:  # 2024年7月25日18:14:18, resize为(width : int, height : int)
            self.image = pygame.transform.scale(self.image, resize)  # 重新调整大小
        self.rect = self.image.get_rect()
        # 2024年7月25日19:11:42, 抓到原因了, 在 draw 里面, surface.blits((spr.image, spr.rect) for spr in sprites)

class Solid(Tile):
    def __init__(self,x = 0, y = 90 ):
        super().__init__(dict_img["solid.png"][0], (TILE,TILE))
        self.rect.bottomleft = (x, y)  # 由于以后怪物的身高问题,所以以后基准都统一成, 从 bottomleft开始画

class Air(Tile):
    def __init__(self,x = 30, y = 90 ):
        super().__init__(dict_img["air.png"][0], (TILE,TILE))
        self.rect.bottomleft = (x, y)

class Trap(Tile):
    def __init__(self,x = 60, y = 90 ):
        super().__init__(dict_img["trap.png"][0], )
        self.rect.bottomleft = (x, y)
        self.dhp = 20  # damage hp = 20

class Ladder(Tile):
    def __init__(self,x = 90, y = 90 ):
        super().__init__(dict_img["ladder.png"][0], )
        self.rect.bottomleft = (x, y)

# class P1_bullet(Sprite):
#     def __init__(self, image = any, speed = 0, x=0, y=0, direction = 0, damage_hp = 10, wall_block = 1, target = None):
#         super().__init__()
#         self.image = image
#         self.speed = speed
#         self.direction = -1 if direction else 1
#         self.rect = self.image.get_rect()
#         self.rect.center = (x+22,y +15)
#         # self.rect.center = (x+200,y +15)
#         self.dhp = damage_hp
#         self.wall_block = wall_block
#         self.t = 0
#
#     def update(self, *args, **kwargs):
#         self.t += 1
#         self.rect.x += (self.direction * self.speed)
#         self.out()
#         if self.wall_block:
#             if spritecollide(self, group_solid, 0): self.kill()
#             # spritecollide(self, group_solid, 1)  # 这样就变成了, 子弹吃掉墙 2024年8月28日15:32:023
#
#     def out(self):
#         if self.rect.right < 0 or self.rect.left > D_width or self.rect.top < 0 or self.rect.bottom > D_height: #放全局的尺寸就对了 2024年8月27日17:58:57
#             self.kill()    #超边界kil;
'''
角色参数: dict  10 args
rm_arges = {'set_shoot_cd': 6, 'g': 2, 'jump_acc': 4, 'jump_time_limit': 12, 'max_speedy': 10, 'max_speedy_up': 10, 'accx': 1, 'spx_limit': 8, 'bullet_sp': 15, 'spx_resistance': 1}
'''
rm_arges = {'set_shoot_cd': 6, 'g': 2, 'jump_acc': 4, 'jump_time_limit': 12, 'max_speedy': 10, 'max_speedy_up': 10, 'accx': 1, 'spx_limit': 8, 'bullet_sp': 15, 'spx_resistance': 1}

class Player(Sprite):  ##复制一个,就可以进其他角色
    def __init__(self, imgs = None, args = rm_arges, bul_fun = None, x=90, y=800, hp = 100, facing = 0):
        super().__init__()
        # 继承属性:
        self.bul = bul_fun
        self.imgs = imgs
        # SURFACE.blit
        self.rect = pygame.Rect(0, 0, 28, 36)
        self.rect.topleft = x, y
        self.hp = hp
        self.speed_x = 0
        self.speed_y = 0
        self.jump_ac = 0
        self.can_jump = 0 # 可以跳, 落地重置
        self.is_ground = 0
        self.invincible_t = 0
        self.can_climb = 0
        self.climbing = 0
        # self.facing = 1   # 面对方向, image的第一维
        self.facing = facing
        self.img_id = 0  #
        self.shooting = 0
        self.can_shoot = 0
        self.shoot_cd = 0
        self.jumping_time = 0
        # 角色相关属性
        self.set_shoot_cd = args['set_shoot_cd']
        self.g = args['g']
        self.jump_acc = args['jump_acc']
        self.jump_time_limit = args['jump_time_limit']
        self.max_speedy = args['max_speedy']
        self.max_speedy_up = args['max_speedy_up']
        self.accx = args['accx']
        self.spx_limit = args['spx_limit']
        self.bullet_sp = args['bullet_sp']
        self.spx_resistance = args['spx_resistance']

    def update(self):
        if self.hp <= 0:
            self.man_die()
            self.kill()
        if self.invincible_t:
            self.invincible_t -= 1
        if self.shoot_cd:  self.shoot_cd -= 1
        else: self.can_shoot = 1
        if self.shooting: self.shooting -= 1
        self.is_ground = 0

        self.control()
        ## image 表现形式
        self.gif()

    def control(self):
        opt = pygame.key.get_pressed()
        # shoot
        if opt[pygame.K_KP1] and self.can_shoot:
            if len(group_p1_bullet) < 3:
                self.shooting = 10
                group_p1_bullet.add(
                    # P1_bullet(image=dict_img['bullet.png'][0], speed=15, x=self.rect.x, y=self.rect.y,  direction=self.facing))
                    self.bul(image=dict_img['bullet.png'][0], speed=self.bullet_sp, x=self.rect.x, y=self.rect.y, direction=self.facing))
                self.shoot_cd = self.set_shoot_cd  # 缩短cd
                self.can_shoot = 0
        # 跳
        if opt[pygame.K_KP2] and self.can_jump:
            self.speed_y -= self.jump_acc
            self.climbing = 0
            self.jumping_time += 1
        elif not opt[pygame.K_KP2]:  # 成功了,只是加了一个松手判定!!!
            # if self.speed_y < 0 :   self.speed_y = 0
            self.can_jump = 0  # 这里成功使得从高处掉落后,不能发起跳跃
        if self.jumping_time > self.jump_time_limit:
            self.can_jump = 0
            self.jumping_time = 0
        # 爬梯子
        if self.can_climb:
            if opt[pygame.K_UP] and opt[pygame.K_DOWN]:
                self.climbing = 1
            elif opt[pygame.K_UP]:
                if t := spritecollide(self, group_ladder, 0):
                    self.rect.left = t[0].rect.left
                    self.img_id += 1
                    self.climbing = 1
                    self.speed_y = -5
            elif opt[pygame.K_DOWN]:
                self.rect.y += 1
                if t := spritecollide(self, group_ladder, 0):
                    self.rect.left = t[0].rect.left
                self.img_id += 1
                self.climbing = 1
                self.speed_y = 5
            elif self.climbing:
                self.speed_y = 0
        if not self.climbing:
            # self.gravity()
            self.speed_y += self.g
            if self.speed_y > self.max_speedy:
                self.speed_y = self.max_speedy
        # if self.speed_y < - (self.max_speedy -2):
        #     self.speed_y = -(self.max_speedy -2)
        if self.speed_y < -(self.max_speedy_up):
            self.speed_y = -(self.max_speedy_up)
        self.rect.y += self.speed_y
        # player 的碰撞判断包括:  enemy,item,  ladder, gate, solid
        if not self.invincible_t and (t := spritecollide(self, group_enemy, 0, )):
            # print(t)  #{<Player Sprite(in 1 groups)>: [<Trap Sprite(in 2 groups)>, <Trap Sprite(in 2 groups)>]}
            # self.hurted(t[self][0])
            self.hurted(t[0])
        if (t := spritecollide(self, group_item, 0)):
            self.useitem()
        # 梯子检查
        if (t := spritecollide(self, group_ladder, 0)):
            self.can_climb = 1
            self.can_jump = 1  # 也允许跳
            self.jumping_time = 0
            # print("po")
            # print(t) #[<Ladder Sprite(in 1 groups)>]
            if len(t) == 1 and t[0].rect.top >= self.rect.bottom - 10 and not opt[
                pygame.K_DOWN]:  # 梯子顶不掉落, 基本成功; 问题,梯子顶向上爬鬼畜
                self.rect.bottom = t[0].rect.top
                self.is_ground = 1
        else:
            self.can_climb = 0
            self.climbing = 0
        if (t := spritecollide(self, group_gate, 0)):
            pass
        if (t := spritecollide(self, group_solid, 0)):  # y方向判断你
            if self.speed_y < 0:  # 说明是向上撞的
                self.can_jump = 0  # 为了立即停跳
                self.speed_y = 2
                self.rect.y = t[0].rect.bottom
            else:
                self.is_ground = 1
                if not opt[pygame.K_KP2]:
                    self.can_jump = 1  # 松手, 重新可以跳
                    self.jumping_time = 0
                self.rect.bottom = t[0].rect.top
        # x分量
        if opt[pygame.K_LEFT] and opt[pygame.K_RIGHT]:
            pass
        elif opt[pygame.K_RIGHT]:
            self.facing = 0
            self.speed_x += self.accx
            self.img_id += 1
        elif opt[pygame.K_LEFT]:
            self.facing = 1
            self.speed_x -= self.accx
            self.img_id += 1
        else:
            if self.speed_x > 0:
                self.speed_x -= self.spx_resistance
            elif self.speed_x < 0:
                self.speed_x += self.spx_resistance
        if self.speed_x > self.spx_limit:
            self.speed_x = self.spx_limit
        if self.speed_x < -self.spx_limit:
            self.speed_x = -self.spx_limit
        # print(self.speed_x)
        if self.rect.x < 0:  # 空气墙...
            self.rect.x = 0
        self.rect.x += self.speed_x
        if not self.invincible_t and (t := spritecollide(self, group_enemy, 0)):  # 这里因为xy方向分解,导致x方向运动需要额外判断一次...
            # 但是把 not self.invincible and  放到前面, 不过不满足,应该就不需要运行后面了; 没错,我用sleep()又测试了一下
            self.hurted(t[0])
        if (t := spritecollide(self, group_solid, 0)):
            if self.speed_x < 0:
                self.rect.x = t[0].rect.right
            if self.speed_x > 0:
                self.rect.right = t[0].rect.left

    def gif(self):
        i_climbshoot, i_climb_gif, i_sr_gif, i_run_gif, i_idleshoot, i_idle, i_js, i_j = self.imgs
        if self.climbing:
            if self.shooting:
                self.image = i_climbshoot[self.facing - 1]
            else:
                self.image = i_climb_gif[self.facing][(self.img_id // 5) % 2]
        elif self.is_ground:
            self.speed_y = 0
            if self.speed_x != 0:
                if self.shooting:
                    self.image = i_sr_gif[self.facing][(self.img_id // 5) % 4]
                else:
                    self.image = i_run_gif[self.facing][(self.img_id // 5) % 4]
            else:
                if self.shooting:
                    self.image = i_idleshoot[self.facing]
                else:
                    self.image = i_idle[self.facing]  # 站立
                self.img_id = 0
        else:  # 那就剩下jumping了
            if self.shooting:
                self.image = i_js[self.facing]
            else:
                self.image = i_j[self.facing]

    def hurted(self, hurted_by = any):
        self.hp -= hurted_by.dhp
        self.invincible_t = 30   # 30帧 无敌时间,也就是一秒钟
        Spark(self)

    def useitem(self):
        pass

    def man_die(self):
        for i in range(8):
            group_jpg.add(Cycle(self.rect.x, self.rect.y, pi*i/4))

class Spark(Sprite):
    def __init__(self, character):
        super().__init__(group_jpg)
        self.image = dict_img["spark.png"][0]
        self.rect = self.image.get_rect()
        self.p = character
        self.timer = self.p.invincible_t

    def update(self):
        self.timer -= 1
        if self.timer <= 0 or self.p.hp <= 0:
            self.kill()
        self.image.set_alpha(self.timer % 2 * 255)
        self.rect.x = self.p.rect.x
        self.rect.y = self.p.rect.y

class Cycle(Sprite):
    def __init__(self, x=0, y=0, angel = 0):
        super().__init__()
        self.image = dict_img["cycle.png"][0]
        self.rect = pygame.Rect(x, y,0,0)
        s = 20
        self.speedx = s * cos(angel)
        self.speedy = s * sin(angel)
        # self.dhp = 0   # 如果放进 子弹group,是会考虑碰撞的,  那么放进group_air不就好了...

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        self.out()

    def out(self):
        if self.rect.right < 0 or self.rect.left > D_width or self.rect.top < 0 or self.rect.bottom > D_height:
            self.kill()
# charachers  rm: rockman
class Rm(Player):
    def __init__(self, imgs = None, args = None, bul_fun = None, x=90, y=800, hp = 100, auto = False, facing = 0):
        super().__init__(imgs = imgs, args = args, bul_fun = bul_fun, x=x, y=y, hp = hp, facing = facing)
        self.auto = auto

    def update(self, *args, **kwargs):
        if self.auto:
            self.auto_move()
        else:
            super().update()

    def auto_move(self):
        pass

class Enemy(Sprite):
    def __init__(self, image = dict_img["player1.png"][0], x = 0, y = 0, hp = 100, dhp = 10, facing = 0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.hp = hp
        self.dhp = dhp
        self.facing = facing
        self.rect.bottomleft = (x,y)
        self.invincible_t = 0

    def update(self, *args, **kwargs):
        if not self.invincible_t and (t := spritecollide(self, group_p1_bullet, 0)):
            self.hp -= t[0].dhp
            for g in t:
                if str(type(g)) == "<class '__main__.P1_bullet'>":g.kill()

            # print(t)  # [<P1_bullet Sprite(in 0 groups)>]
# 飞行炮弹
class E3(Enemy):
    def __init__(self, x, y):
        super().__init__(image=dict_img["e3.png"][0], x=x, y=y, hp=30, dhp=10, facing=1)
        self.speed = 20
        self.spy = 1 #y 方向追踪速度 2024年8月28日15:42:36

    def update(self, *args, **kwargs):
        super().update()
        if self.hp <= 0: self.kill()
        self.rect.x -= self.speed
        # self.rect.y += max(min(P.rect.y - self.rect.y, 2), -2)
        self.rect.y += max(min(P.rect.y - self.rect.y, self.spy), -self.spy)
        if self.rect.x < -100 or self.rect.x > D_width +100:
            self.speed = -self.speed
            self.facing ^= 1
        self.image = dict_img["e3.png"][self.facing - 1]
#钻地炮塔
class E4(Enemy):
    def __init__(self, x, y):
        super().__init__(image=dict_img["e4.png"][0], x=x, y=y, hp=30, dhp=10, facing=1)
        # self.t = 60  # 60帧  (2秒), 切换时间
        self.t_set = 2 * FRAME_PER_SEC  # 这样就是固定2秒 与帧率无关了
        self.t = self.t_set
        self.t_rect = [pygame.Rect(x,y-10, 30,5), pygame.Rect(x,y-30, 30,30)]
        self.t_image = [dict_img["e4.png"][0], dict_img["e4_1.png"][0]]
        self.ind = 0

    def update(self, *args, **kwargs):
        super().update()
        self.t -= 1
        if self.t == 0:
            self.t = self.t_set
            self.ind ^= 1
            if self.ind:
                group_enemy.add(E_bullet(x= self.rect.x, y = self.rect.y - 25, dir = 1), E_bullet(x= self.rect.x, y = self.rect.y - 25, dir = 0))
                # group_enemy.add(E_bullet_1(x= self.rect.x, y = self.rect.y - 25))   # 追加跟踪子弹
            self.rect = self.t_rect[self.ind]
            self.image = self.t_image[self.ind]
            # self.image = pygame.Surface((0,0))  #可以加一种 blind 效果, 让敌人隐身
        if self.hp <= 0: self.kill()

class P1_bullet(Sprite):
    def __init__(self, image = any, speed = 0, x=0, y=0, direction = 0, damage_hp = 10, wall_block = 1, target = None):
        super().__init__()
        self.image = image
        self.speed = speed
        self.direction = -1 if direction else 1
        self.rect = self.image.get_rect()
        self.rect.center = (x+22,y +15)
        # self.rect.center = (x+200,y +15)
        self.dhp = damage_hp
        self.wall_block = wall_block
        self.t = 0

    def update(self, *args, **kwargs):
        self.t += 1
        self.rect.x += (self.direction * self.speed)
        self.out()
        if self.wall_block:
            if spritecollide(self, group_solid, 0): self.kill()
            # spritecollide(self, group_solid, 1)  # 这样就变成了, 子弹吃掉墙 2024年8月28日15:32:023

    def out(self):
        if self.rect.right < 0 or self.rect.left > D_width or self.rect.top < 0 or self.rect.bottom > D_height: #放全局的尺寸就对了 2024年8月27日17:58:57
            self.kill()    #超边界kil;

class E_bullet(P1_bullet):
    def __init__(self, x=0, y=0, dir = 0, dhp = 10):
        super().__init__(image=dict_img['eb.png'][0], speed=20, x=x, y=y, direction=dir, damage_hp=dhp)

    def update(self, *args, **kwargs):
        super().update()

class E_bullet_1(P1_bullet):   # 追身子弹; 成功...
    def __init__(self, speed = 20, x=0, y=0, dhp = 10):
        super().__init__(image=dict_img['eb.png'][0], x=x, y=y)
        theta = atan2(group_p1.rect.centery - self.rect.y, group_p1.rect.centerx - self.rect.x)
        self.speedx = speed * cos(theta)
        self.speedy = speed * sin(theta)

    def update(self, *args, **kwargs):
        self.out()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
# boss class
class Cut_man(Player):
    def __init__(self, x=0 , y=0, auto = 1, hp = 150, facing = 0):
        super().__init__(x = x, y= y , hp = hp,  facing = facing)
        self.auto = auto
        self.states = []   # 动作集式的bot设定,  状态机
        # 0: idle 1: run 2: shoot 3:jump 4: super
        self.dhp = 15
        self.s = 0
        self.t = 30
        # 下面大段抄写 class Player(Sprite):
        self.speed_x = 0
        self.speed_y = 0
        self.g = 1
        self.jump_ac = 0
        self.can_jump = 0  # 可以跳, 落地重置
        self.is_ground = 0
        self.auto = auto
        # self.auto = 0
        self.invincible_t = 0
        self.can_climb = 0
        self.climbing = 0
        # self.facing = 1  # 面对方向, image的第一维
        self.img_id = 0  #
        self.shooting = 0
        self.can_shoot = 0
        self.shoot_cd = 15

    def update(self, *args, **kwargs):
        # super().update()  # 这里不能直接写, 不然继承扣血; 只有auto时继承就好
        if self.hp <= 0:
            self.man_die()
            self.kill()
        if self.invincible_t:
            self.invincible_t -= 1
        if self.shoot_cd:  self.shoot_cd -= 1
        else: self.can_shoot = 1
        if self.shooting: self.shooting -= 1
        self.is_ground = 0

        ###  有很大一部分物理部分,似乎是可以复用的... 哦,也有问题, 因为添加了按键之后有些额外的变量,这些我都需要做区分
        #  2024年6月15日22:12:07, 下一步  把自然物理和 按键控制 区分开.
        if self.auto:
            # super().update()  # 为了给boss 加无敌,这里重写一遍好了...; 或者, 给enemy写两种update, 或者根据条件来写,是否给self.invincible_t
            if not self.invincible_t and (t := spritecollide(self, group_p1_bullet, 0)):
                self.hp -= t[0].dhp
                self.invincible_t = 30
                for g in t:
                    if str(type(g)) == "<class '__main__.P1_bullet'>": g.kill()
            word = BASICFONT1.render(f"{self.hp}", 0, (255, 0, 0))
            game.screen.blit(word, (1830, 0))
            game.screen.blit(dict_img["hp.png"][0], pygame.Rect(1882, 2, 2, 2))  # 没有起到剪裁作用...
            self.img_id += 1   # 自动需要单算这个来加帧
            self.facing = 0 if P.rect.centerx > self.rect.centerx else 1  # facing 有 0 和1
            if self.t:
                self.t -= 1
            else:
                if self.s == 0:  self.s = random.choice([1,2,2,3])
                elif self.s == 1:  self.s = random.choice([2,3])
                elif self.s == 2:  self.s = random.choice([1,3])
                elif self.s == 3:  self.s = random.choice([2])
                self.t = 30
                self.tface = self.facing if self.facing else -1
            if  self.s == 1:
                self.speed_x = -self.tface * 10
                self.jump_ac = 0
            elif self.s == 2:
                if self.can_shoot:
                    group_enemy.add(Cut(x= self.rect.centerx, y = self.rect.y - 5, s = self, target= P ))
                    self.shoot_cd = 30
                    self.can_shoot = 0
                self.speed_x = 0
                self.jump_ac = 0
            elif self.s == 3:
                self.speed_x = -self.tface * 10
                self.jump_ac = 2
            # 移动开始 注意分解
            self.rect.x += self.speed_x
            if self.rect.x > 1890:
                self.rect.x = 1890
            elif self.rect.x < 0:
                self.rect.x = 0
            if (t := spritecollide(self, group_solid, 0, )):
                if self.speed_x < 0:  self.rect.left = t[0].rect.right
                else:                 self.rect.right = t[0].rect.left
            # y
            self.gravity()      # gravity里包括跳跃了, 所以这里写的有问题...
            self.rect.y += self.speed_y
            if (t := spritecollide(self, group_solid, 0, )):     # y方向判断你
                if self.speed_y < 0 :            # 说明是向上撞的
                    self.speed_y = 2
                    self.rect.y = t[0].rect.bottom
                else:
                    self.is_ground = 1
                    self.rect.bottom = t[0].rect.top
            pass
        else:   # 控制部分:
            word = BASICFONT1.render(f"{self.hp}", 0, (0, 255, 0))
            game.screen.blit(word, (30, 0))
            game.screen.blit(dict_img["hp.png"][0], pygame.Rect(2, 2, 2, 2))
            ori_rect = self.rect.copy()  # 记录一下原始位置, 在行动和重力都运行完毕之后, check一下碰撞
            # 尝试拆分 水平和竖直分量
            self.jump_ac = 0
            opt = pygame.key.get_pressed()
            # kp8 debug 也可以用breakpoint
            if opt[pygame.K_KP8]:
                self.image = dict_img["player1.png"][0]
                # self.image = dict_img["background.png"]
                # breakpoint()
                print(1)  ### debug; 放在这里可以了...
            # shoot
            if opt[pygame.K_KP1] and self.can_shoot:
                if len(group_p1_bullet) < 3:
                    self.shooting = 30
                    for g in group_enemy:
                        # if g in group_solid:continue   # trap也算作enemy; 但这不是主要问题,主要问题是, 为什么会打自己?
                        # if g in group_enemy_bullet: continue    # 还有一个问题,甚至回去追踪敌人的子弹 因为也在 group_enemy, 而且没有区分.. 似乎需要重新搞分组了...
                        # 暂时可以利用 bullet 没有hp属性来区分.... 只是权益直接, 最好还是重新分组...
                        # if "hp" not in vars(g): continue
                        if hasattr(g, "hp"):        # 这个更方便, solid和子弹都没有 .hp
                            group_p1_bullet.add(Cut(x=self.rect.centerx, y=self.rect.centery, s = self, target=g))
                    self.shoot_cd = 15
                    self.can_shoot = 0
            # 跳
            if opt[pygame.K_KP2] and self.can_jump:
                self.speed_y -= 4
                self.jump_ac = 3
                self.climbing = 0
            elif not opt[pygame.K_KP2]:  # 成功了,只是加了一个松手判定!!!
                # 立即停止上升
                if self.speed_y < 0:   self.speed_y = 0
                self.can_jump = 0  # 这里成功使得从高处掉落后,不能发起跳跃
            # 爬梯子
            if self.can_climb:
                if opt[pygame.K_UP] and opt[pygame.K_DOWN]:
                    self.climbing = 1
                elif opt[pygame.K_UP]:
                    self.img_id += 1
                    self.climbing = 1
                    self.speed_y = -5  # 写这个速度没有用,因为和我写的 跳跃松手产生了冲突...
                elif opt[pygame.K_DOWN]:
                    self.img_id += 1
                    self.climbing = 1
                    self.speed_y = 5
                elif self.climbing:
                    self.speed_y = 0

            if not self.climbing:     self.gravity2()
            self.rect.y += self.speed_y
            if not self.invincible_t and (t := spritecollide(self, group_enemy, 0)):
                self.hurted(t[0])
            if (t := spritecollide(self, group_item, 0, )):
                self.useitem()
            # 梯子检查
            if (t := spritecollide(self, group_ladder, 0, )):
                self.can_climb = 1
                self.can_jump = 1  # 也允许跳
            else:
                self.can_climb = 0
                self.climbing = 0
            if (t := spritecollide(self, group_gate, 0, )):
                pass
            # 下面的 print(t) #{<Player Sprite(in 1 groups)>: [<Trap Sprite(in 1 groups)>, <Trap Sprite(in 1 groups)>]}
            if (t := spritecollide(self, group_solid, 0, )):  # y方向判断你
                if self.speed_y < 0:  # 说明是向上撞的
                    self.can_jump = 0
                    self.speed_y = 2
                    self.rect.y = t[0].rect.bottom
                else:
                    self.is_ground = 1
                    if not opt[pygame.K_KP2]:  self.can_jump = 1  # 松手, 重新可以跳
                    self.rect.bottom = t[0].rect.top
            # x分量
            self.speed_x = 0
            if opt[pygame.K_LEFT] and opt[pygame.K_RIGHT]:
                pass
            elif opt[pygame.K_RIGHT]:
                self.facing = 0
                self.speed_x = 5
                self.img_id += 1
            elif opt[pygame.K_LEFT]:
                self.facing = 1
                self.speed_x = -5
                self.img_id += 1
            # 边界限定
            # if self.rect.x > 1890:
            #     self.rect.x = 1890
            if self.rect.x < 0:
                self.rect.x = 0
            self.rect.x += self.speed_x
            if not self.invincible_t and (t := spritecollide(self, group_enemy, 0)):  # 这里因为xy方向分解,导致x方向运动需要额外判断一次...
                self.hurted(t[0])
            if (t := spritecollide(self, group_solid, 0, )):
                self.rect.x = ori_rect.x  # x方向因挡路而回正

        ## image 表现形式
        if self.climbing:
            if self.shooting:
                self.image = dict_img["cm_shoot2.png"][(self.facing - 1)]
            else:
                self.image = dict_img["cm_jump.png"][(self.facing - 1)]
        elif self.is_ground:
            self.speed_y = 0
            if self.speed_x != 0:
                if self.shooting:
                    self.image = d_cm_sr[(self.facing)^1][(self.img_id // 5) % 4]
                else:
                    self.image = d_cm_run[(self.facing)^1][(self.img_id // 5) % 4]
            else:
                if self.shooting:
                    self.image = dict_img["cm_shoot1.png"][(self.facing)^1]
                else:
                    self.image = dict_img["cm_idle.png"][(self.facing)^1]  # 站立
                self.img_id = 0
        else:  # 那就剩下jumping了
            if self.shooting:
                self.image = dict_img["cm_shoot2.png"][(self.facing)^1]
            else:
                self.image = dict_img["cm_jump.png"][(self.facing)^1]
        if self.invincible_t and self.invincible_t % 2:
            SURFACE.blit(dict_img["spark.png"][0], self.rect)

    def gravity(self):
        self.speed_y += self.g - self.jump_ac
        if self.speed_y > 10:
            self.speed_y = 10
        elif self.speed_y < -4:
            self.can_jump = 0
            self.speed_y = -4

    def gravity2(self):  #atuo = 0 单写
        Jsp = 12
        self.speed_y += self.g - self.jump_ac
        if self.speed_y > 10:
            self.speed_y = 10
        elif self.speed_y < -Jsp:
            self.can_jump = 0
            self.speed_y = -Jsp
        # def check_collision_solid(self):
        #     return groupcollide(group_p1, group_solid, 0, 0)

    def hurted(self, hurted_by=any):
        self.hp -= hurted_by.dhp
        self.invincible_t = 30  # 30帧 无敌时间,也就是一秒钟

    def useitem(self):
        pass

    def man_die(self):
            for i in range(8):
                group_jpg.add(Cycle(self.rect.x, self.rect.y, pi*i/4))
            self.kill()

class Cut(P1_bullet):
    def __init__(self, speed = 20, x=0, y=0, dhp = 15, s = any, target = group_p1):
        super().__init__(image=dict_img['cmb0.png'][0], x=x, y=y, damage_hp=dhp)
        theta = atan2(target.rect.centery - self.rect.y, target.rect.centerx - self.rect.x)
        self.speedx = speed * cos(theta)
        self.speedy = speed * sin(theta)
        self.t = 0
        self.s = s

    def update(self, *args, **kwargs):
        self.t += 1
        self.image = [dict_img['cmb0.png'][0],dict_img['cmb1.png'][0],dict_img['cmb0.png'][1],dict_img['cmb1.png'][1]][self.t%4]
        if self.t <=20:
            self.rect.x += self.speedx
            self.rect.y += self.speedy
        elif self.t <= 50:
            pass
        else:
            self.rect.x += max(min(self.s.rect.x - self.rect.x, 10), -10)
            self.rect.y += max(min(self.s.rect.y - self.rect.y, 10), -10)
            self.eat()

    def eat(self):
        if spritecollide(self, [self.s], 0):
            self.kill()
            # self.s.kill()

# menu; 先也用Sprite试试看   #  2024年8月28日21:21:42, 修改成可缩放大小;  方法: 先放到一个surface上,然后按比例缩放surface
class Menu(Sprite):
    def __init__(self, ):
        super().__init__()
        self.image = pygame.Surface((D_width, D_height)).convert_alpha()
        # self.image = pygame.Surface((D_width, D_height), pygame.SRCALPHA).convert_alpha()
        self.image.fill((0, 0, 0, 0))  # 透明背景  2024年8月30日08:58:22, 这里是必要的...  有点搞不懂了...
        self.rect = (0,0,0,0)
        self.p = 0
        self.d = {0:[True, "rockman", (970, 370)], 1:[True, "cutman",(970, 400)], 2:[False, "boomman",(970, 430)], 3:[False, "boomman",(970, 460)],
            4: [False, "boomman", (970, 490)],5:[False, "boomman",(970, 520)],6:[False, "boomman",(970, 550)],7:[False, "boomman",(970, 580)]
                  }
        self.keydown_up = self.keydown_down = True
        self.bg = dict_img["menu.png"][0]
        self.bg.set_alpha(50)
        self.bg_flag = 1
    # 2024年8月30日09:06:20 ,找到问题了, 菜单的重绘调用update不合理,因为菜单这个都是没没有必要每一帧的重新画的,而是应该接受变化,只有变化后才重绘, 否则就浪费了cpu; 2024年9月2日21:43:20,先不修改...
    def update(self, *args, **kwargs):
        global P
        # self.image.set_alpha(20)  # 这个东西这样写,是叠加的 2024年8月29日21:52:16
        self.image.fill((0,0,0, 0))
        if self.bg_flag:
            # self.bg_flag = 0
            m = self.bg
            self.image.blit(m , (500,200))
        word = BASICFONT1.render("HP: " + f"{P.hp}", 0, (0, 255, 0))
        # print(P1, P1.hp)  # 似乎kill并不是把sprite删除了,而是把sprite从所有groups里扔了, 自身还存在,但是不会update了
        self.image.blit(word, (600, 400))
        w0 = BASICFONT1.render("ROCKMAN", 0, (0, 255, 0))
        self.image.blit(w0, (1000, 360))
        w0 = BASICFONT1.render("CUTMAN", 0, (0, 255, 0))
        self.image.blit(w0, (1000, 390))
        # 2024年6月15日15:42:29 菜单, 施工到中途, 先去写第一个boss了 剪刀人吧
        opt = pygame.key.get_pressed()
        # keydown = True
        if opt[pygame.K_UP] and self.keydown_up:
            self.p = (self.p - 1)%7
            self.keydown_up = 0
        elif opt[pygame.K_DOWN]and self.keydown_down:
            self.p = (self.p + 1)%7
            self.keydown_down = 0
        if not opt[pygame.K_UP]:self.keydown_up = 1
        if not opt[pygame.K_DOWN]:self.keydown_down = 1
        self.image.blit(dict_img['bullet.png'][0], self.d[self.p][2])
        if opt[pygame.K_KP1]:
            game.menu ^= 1
            if self.p == 0:
                P.kill()
                P = Rm(x= P.rect.x, y= P.rect.y, hp = P.hp, facing= P.facing, imgs=rock_imgs, bul_fun=P1_bullet, args=rm_arges, auto=0)
                group_p1.add(P)
            if self.p == 1:
                P.kill()
                P = Cut_man(x= P.rect.x, y= P.rect.y , hp= P.hp, auto = 0, facing= P.facing)
                group_p1.add(P)
            # ↓  尝试删除,成功
            if self.p == 2:
                for g in group_all_list:
                    if g == group_bg: continue
                    for x in g:
                        # if x == P1:continue
                        x.kill()



# class 主程序
class Leetman:
    def __init__(self):
        pygame.init()
        self.screen = SURFACE
        self.clock = pygame.time.Clock()
        self.create_sprites()
        self.restart = 0
        self.menu = 0
        self.t = 1   # 用来判定死亡  后期还是改回play_group吧...
        self.size = SCREEN.get_size()
        self.menu_surface = pygame.Surface((D_width, D_height), pygame.SRCALPHA)  # pygame.SRCALPHA 还是需要的,才能透明  而不加这个.fill((0, 0, 0, 0))也没用...
        # self.menu_surface.fill((0, 0, 0, 0))

    def create_sprites(self):
        # global group_p1, P  # 因为敌人要寻找主角位置, 所以这里添加了一个全局变量.  反正主角永远只有一个
        global P
        bg = Tile(dict_img["background.png"][1], (D_width, D_height))
        group_bg.add(bg)
        P = Rm(x= 20, y= 900, hp = 99, imgs = rock_imgs, bul_fun= P1_bullet, args = rm_arges, auto = 0)
        group_p1.add(P)
        create_map(maps[0])
        # menu
        group_menu.add(Menu())

    def game_loop(self):
        while True:
            if self.restart: return
            # SURFACE.fill((0, 0, 0))
            self.clock.tick(FRAME_PER_SEC)
            # self.clock.tick(30)    #在这里修改fps一样的
            pygame.display.set_caption('FPS = ' + str(self.clock.get_fps())[:5])
            # pygame.display.set_caption('FPS = ' + str(pygame.time.Clock().get_fps())[:5])  #2024年9月6日18:07:10, 错误的 Clock() 需要在外面定义好,不能重复来定义; 像一个初始锚点
            # pygame.display.set_caption('FPS = ' + str(self.clock.get_fps())[:5] +" can jump = " +str(bool(P.can_jump)))
            self.event_handler()
            if not self.menu:
                self.update_gaming_sprites()
                if P.rect.x > 1910:
                    if len(maps) > 1:
                    # if 1:
                        maps.pop(0)
                        self.dele()
                        group_bg.add(Tile(dict_img["background.png"][1], (D_width, D_height)))
                        create_map(maps[0])
                        P.rect.bottomleft = (-10, 31 * 30)
                SCREEN.fill((0, 0, 0))
                # dx = SCREEN.get_width() // 2 - P.rect.centerx
                dx = self.size[0] // 2 - P.rect.centerx
                dy = self.size[1] // 2 - P.rect.centery
                if dx > 0: dx = 0
                if dy > 0: dy = 0
                if dx < (t := self.size[0] - 1920): dx = t
                if dy < (t := self.size[1] - 990): dy = t
                SCREEN.blit(SURFACE, (dx, dy))
                word = BASICFONT1.render(f"{P.hp}", 0, (0, 255, 0)) # 2024年9月8日14:50:34主角的血条显示( 写在这里其实也不合适,应该包起来的)
                SCREEN.blit(word, (30, 0))
                SCREEN.blit(dict_img["hp.png"][0], (2, 2), pygame.Rect(0, 0, 18, 200))  # 2024年8月22日23:00:47, 可以剪裁了, 可以配合fun使用, 再加一个外框
            else:
                self.update_menu()

            pygame.display.flip()


    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_KP9:
                    exit()
                elif event.key == pygame.K_KP7:
                    self.restart = 1
                    for g in group_menu: g.kill()
                elif event.key == pygame.K_KP6:
                    maps.pop(0)
                elif event.key == pygame.K_KP8:
                    # breakpoint()  #放这个没事,比pycharm的dibug强...
                    print(1)  # debug 位置  ; 放在这里有bug
                # elif event.key == pygame.K_RIGHT:
                #     P.speed_x = 10
                elif event.key == pygame.K_KP5:
                    # self.menu_surface.fill((0, 0, 0, ))  # 还是没用? 没有渐变
                    self.menu ^= 1  # 暂停&菜单
            elif event.type == pygame.VIDEORESIZE:
                self.size = width, height = event.size[0], event.size[1]  # 获取新的size

    def update_gaming_sprites(self):
        for g in group_all_list:
            ## 这里改变一下顺序, 先draw 再 update 这样 update里面 blit的图片就能 出现在 draw的sprite.image上面
            # 这样造成的问题就是, 实际上图片是滞后一帧的, 但是影响很不明显
            g.update()
            g.draw(SURFACE)

    def update_menu(self):
        group_menu.draw(self.menu_surface)
        SCREEN.blit(pygame.transform.scale(self.menu_surface, (self.size[0], self.size[1])), (0, 0))
        # SCREEN.blit(self.menu_surface, (0, 0))
        # group_menu.draw(SURFACE)
        group_menu.update()

    def dele(self):         # 清理所有sprite
        for g in group_all_list:
            if g == group_p1: continue
            for s in g:
                s.kill()

#####
if __name__ == '__main__':
    while 1:
        game = Leetman()
        game.game_loop()
        game.dele()
        P.kill()





