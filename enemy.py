import pyxel
from enum import IntEnum
from values import (FPS,
                    CELL_SIZE,
                    MARGIN,
                    PLAY_BOTTOM_LINE,
                    GamePlay,
                    GameObject)

DT = 1 / (FPS / 2)
G = 9.8
# 敵種類追加得点区切り
ENEMY_ADD_POINT = 1000


class EnemyType(IntEnum):
    UFO = 0
    Normal = 1
    Lite = 2
    Hevy = 3


class Enemy(GameObject):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.h = CELL_SIZE
        self.w = CELL_SIZE
        if self.type == EnemyType.UFO:
            self.w = 32
        # 落下用パラメータ
        self.vec = 0                        # vector
        self.vel = 0                        # velciity
        self.g = G                          # 重力加速度
        self.Life = 180                     # 生存力
        self.rote = 10
        if self.type == EnemyType.Lite:
            self.g = G / 2
            self.rote = 45
        elif self.type == EnemyType.Hevy:
            self.g = G * 2
            self.rote = 90

    def update(self):
        if self.pos.y + self.h < PLAY_BOTTOM_LINE:
            # 落下中
            # f = self.weight * self.g
            # a = f / self.weight
            self.vel += self.g * DT
            self.pos.y += self.vel * DT
        else:
            # 着地後
            if self.type == EnemyType.Hevy:
                self.Life -= 1
            else:
                self.y = PLAY_BOTTOM_LINE + self.h


class EnemyManager:
    def __init__(self, enemy_img_idx):
        self.img_idx = enemy_img_idx
        self.items = []

        self.UFO = Enemy(0)
        self.next_UFO_pos = pyxel.width / 2 - self.UFO.w / 2
        self.UFO.pos.x = self.next_UFO_pos
        self.move_UFO_DIRC = False

    def update(self, state: GamePlay, score: int):
        if state is not GamePlay.Play:
            return
        if self.UFO.pos.x == self.next_UFO_pos:
            # 次の移動先を決める
            self.UFONextPos()
            # 敵落とす
            r = int(score / ENEMY_ADD_POINT)
            t = 1
            if 1 < r:
                t = pyxel.rndi(1, min(int(EnemyType.Hevy), r))
            enmy = Enemy(t)
            enmy.pos.x = self.UFO.pos.x + self.UFO.w / 4
            enmy.pos.y = self.UFO.pos.y + self.UFO.h
            self.items.append(enmy)
        else:
            self.UFOMove()

        for e in self.items:
            e.update()

        # 落下した敵 地面より下にいるものの削除
        tmp = []
        while self.items:
            e = self.items.pop()
            if e.type == EnemyType.Hevy:
                if 0 < e.Life:
                    tmp.append(e)
            else:
                if e.pos.y <= PLAY_BOTTOM_LINE:
                    tmp.append(e)
        while tmp:
            self.items.append(tmp.pop())

    def draw(self):
        pyxel.blt(self.UFO.pos.x, self.UFO.pos.y, self.img_idx,
                  self.UFO.u, self.UFO.v, self.UFO.w, self.UFO.h,
                  colkey=pyxel.COLOR_GRAY)
        for e in self.items:
            # Todo:　グラフィック
            pyxel.blt(e.pos.x, e.pos.y,
                      1, 0, 0, 16, 16,
                      colkey=pyxel.COLOR_GRAY,
                      rotate=e.rote)

    def UFOMove(self):
        '''
        UFO 移動
        '''
        if self.UFO.pos.x < self.next_UFO_pos:
            self.UFO.pos.x += 1
        else:
            self.UFO.pos.x -= 1

    def UFONextPos(self):
        '''
        UFO移動先
        '''
        left = MARGIN
        right = pyxel.width - MARGIN - self.UFO.w
        length = pyxel.rndi(left, right)

        if self.move_UFO_DIRC is False:
            # 左へ
            self.next_UFO_pos -= length
            if self.next_UFO_pos < left:
                self.next_UFO_pos = left
            self.move_UFO_DIRC = True
        else:
            # 右へ
            self.next_UFO_pos += length
            if right < self.next_UFO_pos:
                self.next_UFO_pos = right
            self.move_UFO_DIRC = False

    def Reset(self):
        self.items.clear()
        self.UFO.pos.x = self.UFO.pos.x + self.UFO.w / 4
