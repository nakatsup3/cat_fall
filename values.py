from enum import Enum

WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
FPS = 60

# 1マス分のサイズ
CELL_SIZE = 16
# 左右に設けるプレイヤー安全領域
MARGIN = int(CELL_SIZE / 2)

# 横切った時の得点
ONE_PLAY_SCORE = 10
# スコアボードの上辺の位置
SCORE_BOARD_LINE = WINDOW_HEIGHT - CELL_SIZE * 2
# プレイヤーの描画位置
PLAY_BOTTOM_LINE = SCORE_BOARD_LINE - MARGIN

# 扉開閉
CLOSE = False
OPEN = True


class GamePlay(Enum):
    Title = 0
    Play = 1
    PlayStop = 2
    PlayReset = 3
    Pose = 4
    GameOverPre = 5
    GameOver = 6


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class GameObject:
    def __init__(self):
        self.pos = Vec2(0, 0)
        self.u = 0
        self.v = 0
        self.w = 0
        self.h = 0
