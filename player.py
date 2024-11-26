import pyxel
from enum import Enum
from math import (e, log)
from values import (FPS,
                    CELL_SIZE,
                    MARGIN,
                    PLAY_BOTTOM_LINE,
                    CLOSE,
                    ONE_PLAY_SCORE,
                    GamePlay)

# プレイヤー開始位置
START_POS = MARGIN * -1
# プレイヤーの疲れMAX値
PLAYER_FATIGUE_MAX = 9999

# キャラクタの向き
LEFT = 1
RIGHT = -1

# 小ジャンプ高さ
JUMP_MIN_H = 16


class PState(Enum):
    Walk = 0
    Jump = 1


class Player:
    def __init__(self, player_img_idx):
        self.x = START_POS
        self.y = PLAY_BOTTOM_LINE - CELL_SIZE
        # 動作用
        self.direction = RIGHT              # キャラ向き
        self.fatigue = 1                    # 疲れ値
        self.img_index = player_img_idx     # キャラ画像のライブラリインデックス
        self.active_idx = 0                 # キャラ動き
        self.speed = 2
        # ジャンプ用
        self.state = PState.Walk
        self.t = 0                  # from 0 to 1
        self.height = JUMP_MIN_H    # ジャンプ高さ
        self.jmp_lock = False       # ジャンプ上昇ロック

    def update(self, game_play: GamePlay, is_open: bool):
        '''
        更新
        '''
        if game_play is not GamePlay.Play:
            # プレイ中以外は操作しない
            return 0
        # debug
        if pyxel.btnp(pyxel.KEY_UP):
            self.fatigue += 1
            self.speed = self.speed * (1 - self.fatigue * 0.1)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.fatigue -= 1
            self.speed = self.speed * (1 - self.fatigue * 0.1)
        # debug

        if self.state == PState.Walk:
            # ジャンプ状態へ
            if self.PressJump() and 0 < self.x:
                self.state = PState.Jump
        elif self.state == PState.Jump:
            self.Jump()

        # 移動とスコア計算
        if self.PressLeft():
            self.direction = LEFT
            self.x -= self.speed
            # ドア当たり判定
            if self.x < MARGIN:
                self.x = MARGIN

        door = pyxel.width - MARGIN - CELL_SIZE
        if self.PressRight():
            self.direction = RIGHT
            if self.x < 0:
                # 最初の一歩
                self.x = MARGIN
            else:
                self.x += self.speed
            # ドア当たり判定
            if (is_open is CLOSE and door <= self.x) \
                    or (door <= self.x and self.state is PState.Jump):
                self.x = door

        # 右端到達ポイント判定
        if door + CELL_SIZE <= self.x:
            return ONE_PLAY_SCORE * self.FatiguePoint()
        return 0

    def draw(self):
        '''
        描画
        '''
        img_u = CELL_SIZE * self.active_idx
        pyxel.blt(self.x, self.y, self.img_index,
                  img_u, 0, CELL_SIZE * self.direction, CELL_SIZE,
                  colkey=pyxel.COLOR_GRAY)

    def Jump(self):
        '''
        ジャンプの現在値を計算する
        '''
        if self.PressJump() and self.jmp_lock is False:
            self.height = min(40, self.height + 1)
        self.t += 1 / FPS
        self.y = PLAY_BOTTOM_LINE \
            + (self.height * e * self.t * log(self.t)) - CELL_SIZE

        if 1 < self.t:
            self.y = PLAY_BOTTOM_LINE - CELL_SIZE
            self.t = 0
            if self.state == PState.Jump:
                self.jmp_lock = False
                self.height = JUMP_MIN_H
                self.state = PState.Walk

    def PressLeft(self):
        '''
        操作 左
        '''
        if pyxel.btn(pyxel.KEY_LEFT) \
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            return True
        return False

    def PressRight(self):
        '''
        操作 右
        '''
        if pyxel.btn(pyxel.KEY_RIGHT) \
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            return True
        return False

    def PressJump(self):
        '''
        操作 ジャンプ
        '''
        if pyxel.btnr(pyxel.KEY_SPACE):
            self.jmp_lock = True
            return False
        if pyxel.btn(pyxel.KEY_SPACE) \
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            return True
        return False

    def FatiguePoint(self):
        return self.fatigue

    def AddFatigue(self):
        self.fatigue += 1
        self.speed = self.speed * (1 - self.fatigue * 0.1)

    def ResetPos(self):
        '''
        プレイヤーリセット
        '''
        self.speed = 2
        self.fatigue = 0
        self.x = START_POS
        self.y = PLAY_BOTTOM_LINE - CELL_SIZE
        self.t = 0
        self.state = PState.Walk
