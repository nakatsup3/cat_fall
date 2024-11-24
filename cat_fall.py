import pyxel
import random
from enum import Enum

# ウインドウ設定
WINDOW_HEIGHT = 256
WINDOW_WIDTH = 256
TITLE = 'MainWindow'
FPS = 60

# 1マス分のサイズ
CELL_SIZE = 16
# 左右に設けるプレイヤー安全領域
MARGIN = int(CELL_SIZE / 2)
# スコアボードの上辺の位置
SCORE_BOARD_LINE = WINDOW_HEIGHT - CELL_SIZE * 2
# プレイヤーの描画位置
PLAY_BOTTOM_LINE = SCORE_BOARD_LINE - MARGIN
# 敵が落ちて消える位置
DROP_LINE = PLAY_BOTTOM_LINE - CELL_SIZE * 10

# 左右マージン分を差し引いた横の配置数
GRID_COL = int(WINDOW_WIDTH / CELL_SIZE) - 1

# 横切った時の得点
ONE_PLAY_SCORE = 10
# プレイヤー開始位置
START_POS = int(CELL_SIZE / 2) * -1
# プレイヤーの疲れMAX値
PLAYER_WAIT_MAX = 9999

# 落下時の停止間隔
DRAW_INTERVAL = 45

# キャラクタの向き
LEFT = 1
RIGHT = -1


class GamePlay(Enum):
    Title = 0
    Play = 1
    PlayStop = 2
    Pose = 3
    GameOverPre = 4
    GameOver = 5


class EnemyType(Enum):
    UFO = 0
    Type1 = 1

    # etc ... いろいろ作る。


class Player:
    def __init__(self):
        self.x = START_POS
        self.y = PLAY_BOTTOM_LINE - CELL_SIZE
        self.direction = RIGHT
        self.wait = 0
        self.wait_count = 0

    def update(self, game_play, is_open):
        if game_play is not GamePlay.Play:
            # プレイ中以外は操作しない
            return 0

        # だんだん足が重くなる 
        self.wait_count += 2
        wait = int(self.wait / 10) * 10
        if self.wait_count < wait:
            return 0

        score = 0
        if self.PressLeft():
            self.direction = LEFT
            self.x -= CELL_SIZE
            # ドア当たり判定
            if self.x < MARGIN:
                self.x = MARGIN
            else:
                score = 1
                self.wait_count = 0
                self.wait = min(PLAYER_WAIT_MAX, self.wait + 1)

        if self.PressRight():
            self.direction = RIGHT
            if self.x < 0:
                # 最初の一歩
                self.x = MARGIN
            else:
                self.x += CELL_SIZE
            # ドア当たり判定
            door = pyxel.width - MARGIN - CELL_SIZE
            if is_open is False and door <= self.x:
                # 当たっている
                self.x = door
            else:
                # 当たってない
                self.wait_count = 0
                score = 1
                self.wait = min(PLAYER_WAIT_MAX, self.wait + 1)

        # 右端到達ポイント判定
        if pyxel.width <= self.x:
            return ONE_PLAY_SCORE
        return score

    def ResetPos(self):
        '''
        プレイヤーリセット
        '''
        self.wait = 0
        self.x = START_POS

    def PressLeft(self):
        '''
        操作 左
        '''
        if pyxel.btnp(pyxel.KEY_LEFT) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            return True
        return False
    
    def PressRight(self):
        '''
        操作 右
        '''
        if pyxel.btnp(pyxel.KEY_RIGHT) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            return True
        return False

class Enemy:
    def __init__(self, x, y, speed, type):
        self.x = x              # 描画位置 x
        self.y = y              # 描画位置 y
        self.speed = speed      # 落下速度
        self.type = type        # 敵種別

    def update(self):
        '''
        更新 落下処理
        '''
        self.y = min(pyxel.height,
                     self.y + self.speed)
        if PLAY_BOTTOM_LINE - CELL_SIZE < self.y:
            self.y = pyxel.height


def isHit(player, enemy):
    '''
    当たり判定
    '''
    l1 = player.x
    t1 = player.y
    r1 = player.x + CELL_SIZE
    b1 = player.y + CELL_SIZE

    l2 = enemy.x
    t2 = enemy.y
    r2 = enemy.x + CELL_SIZE
    # 落ちる前に判定するので一段下まで判定を伸ばす
    b2 = enemy.y + CELL_SIZE * 2
    if r2 > l1 and r1 > l2 \
            and b2 > t1 and b1 > t2:
        return True  # ヒット
    return False  # ヒットなし


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT,
                   title=TITLE, fps=FPS)
        self.init()
        pyxel.run(self.update, self.draw)

    def init(self):
        '''
        ゲーム内部変数初期化
        '''
        # リソース読込み
        pyxel.mouse(False)
        pyxel.images[0].load(0, 0, 'assets/Pallet.png', incl_colors=True)
        pyxel.images[1].load(0, 0, 'assets/cat_l_16x16.png')
        pyxel.images[2].load(0, 0, 'assets/ufo.png')
        self.fnt_jp_10 = pyxel.Font("assets/umplus_j10r.bdf")

        self.game_satate = GamePlay.Title
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.score_count = 0
        self.interval = 0
        self.swipe = 0
        self.right_door = True      # true 開く, false 閉じる
        self.door_wait = 0          # 閉じている時間
        self.door_wait_count = 0    # 閉じてからの経過時間
        self.ufo = Enemy(MARGIN, CELL_SIZE, 0, EnemyType.UFO)

    def update(self):
        '''
        データ更新
        '''
        if self.game_satate == GamePlay.Title:
            # ゲームスタート
            if pyxel.btnp(pyxel.KEY_SPACE) \
                    or self.GamePadPushAnyKey():
                self.game_satate = GamePlay.Play

        elif self.game_satate == GamePlay.Play:
            # 一時停止
            if pyxel.btnp(pyxel.KEY_SPACE) \
                    or self.GamePadPushAnyKey():
                self.game_satate = GamePlay.Pose
                return

            self.interval += 1

            # プレイヤー移動
            s = self.player.update(self.game_satate, self.right_door)
            if ONE_PLAY_SCORE <= s:
                self.game_satate = GamePlay.PlayStop
            else:
                self.score += s

            # 敵がカクカク落ちる演出
            if DRAW_INTERVAL < self.interval:
                for e in self.enemies:
                    if isHit(self.player, e) is False:
                        e.update()
                    else:
                        self.game_satate = GamePlay.GameOverPre

                # ufo移動に合わせて敵を降らす
                # 要調整 ゲームバランス 乱数での敵追加
                if 30 < random.randrange(0, 100):
                    x = MARGIN + random.randrange(0, GRID_COL) * CELL_SIZE
                    self.ufo.x = x
                    self.enemies.append(
                        Enemy(x, DROP_LINE, CELL_SIZE, EnemyType.Type1))

                # 要調整 ドア開閉
                if self.door_wait < self.door_wait_count:
                    self.right_door = True
                    # 10%の確率で閉まる　ドア上にプレイヤーがいるときは閉まらない
                    if random.randrange(0, 100) < 10:
                        self.right_door = False
                        self.door_wait = random.randrange(0, 10)
                        self.door_wait_count = 0
                        # ドア上にいたら締め出す
                        door = pyxel.width - MARGIN
                        if door <= self.player.x:
                            self.player.x = door - CELL_SIZE
                else:
                    self.door_wait_count += 1

                # 落下した敵 地面より下にいるものの削除
                tmp = []
                while self.enemies:
                    e = self.enemies.pop()
                    if e.y < pyxel.height:
                        tmp.append(e)
                while tmp:
                    self.enemies.append(tmp.pop())

                self.interval = 0

        elif self.game_satate == GamePlay.PlayStop:
            # 得点増加演出
            self.score_count += 1
            if ONE_PLAY_SCORE < self.score_count:
                self.score += ONE_PLAY_SCORE * int(self.player.wait / 10)
                self.score_count = 0
                self.player.ResetPos()
                self.game_satate = GamePlay.Play

        elif self.game_satate == GamePlay.Pose:
            # 一時停止解除
            if pyxel.btnp(pyxel.KEY_SPACE) \
                    or self.GamePadPushAnyKey():
                self.game_satate = GamePlay.Play

        elif self.game_satate == GamePlay.GameOverPre:
            # 画面上下から黒幕で画面を覆う演出
            self.swipe += 1
            if 130 < self.swipe:
                self.swipe = 0
                self.game_satate = GamePlay.GameOver

        elif self.game_satate == GamePlay.GameOver:
            if pyxel.btnp(pyxel.KEY_SPACE) \
                    or self.GamePadPushAnyKey():
                self.enemies.clear()
                self.score = 0
                self.player.ResetPos()
                self.ufo.x = MARGIN
                self.game_satate = GamePlay.Title

    def draw(self):
        '''
        描画更新
        '''
        if self.game_satate != GamePlay.GameOver:
            # ゲームオーバー時以外の共通描画
            pyxel.cls(pyxel.COLOR_LIGHT_BLUE)
            self.DrawBackground()
            self.DrawPlayer()
            self.DrawEnemy()

        if self.game_satate == GamePlay.Title:
            self.DrawMsgCenter('Press the button to start playing',
                               pyxel.height / 2, pyxel.COLOR_BLACK)
            
        if self.game_satate == GamePlay.Pose:
            # ポーズ　画面を黒の半透明で覆う
            pyxel.dither(0.5)
            pyxel.rect(0, 0, pyxel.width, SCORE_BOARD_LINE,
                       pyxel.COLOR_BLACK)
            pyxel.dither(1.0)
            self.DrawMsgCenter('Pose', pyxel.height / 2,
                               pyxel.COLOR_WHITE)

        if self.game_satate == GamePlay.GameOverPre:
            # 上下からの画面覆う演出
            self.DrawSwipe()

        if self.game_satate == GamePlay.GameOver:
            pyxel.cls(pyxel.COLOR_BLACK)
            self.DrawGameOver()

        # スコアボード固定表示
        self.DrawScoreBoard()

        # if self.right_door is False:
        #    self.DrawMsgCenter(f'{self.door_wait}, {self.door_wait_count}', 0,
        #                       pyxel.COLOR_BLACK)

    def GamePadPushAnyKey(self):
        '''
        ゲームパッドいずれかのキーを押す
        '''
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            return True
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            return True
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
            return True
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            return True
        return False

    def DrawMsgCenter(self, msg: str, y_offset: float, col: int = None):
        '''
        中央ぞろえでテキストを描画。高さは任意。
        '''
        if col is None:
            col = pyxel.COLOR_BLACK
        x = pyxel.width / 2 - self.fnt_jp_10.text_width(msg) / 2
        pyxel.text(x, y_offset, msg, col=col, font=self.fnt_jp_10)

    def DrawBackground(self):
        '''
        背景描画
        '''
        # 地面 奥行
        pyxel.rect(0, SCORE_BOARD_LINE - CELL_SIZE * 2,
                   pyxel.width, CELL_SIZE * 2, pyxel.COLOR_BROWN)

        wall_width = CELL_SIZE * 2
        deps = CELL_SIZE * 2
        wall_height = SCORE_BOARD_LINE - deps - CELL_SIZE
        # 左壁
        pyxel.tri(0, CELL_SIZE, wall_width, deps, 0, deps,
                  pyxel.COLOR_LIME)
        pyxel.rect(0, deps, wall_width, wall_height,
                   pyxel.COLOR_LIME)
        pyxel.tri(0, wall_height + deps, wall_width, wall_height + deps,
                  0, SCORE_BOARD_LINE, pyxel.COLOR_LIME)

        door_w = CELL_SIZE
        door_h = CELL_SIZE * 2
        door_y = SCORE_BOARD_LINE - door_h - MARGIN

        # 左出入口
        door_l_col = pyxel.COLOR_NAVY
        if 0 <= self.player.x:
            # 外に出ると扉を閉じる
            door_l_col = pyxel.COLOR_GREEN
        pyxel.tri(0, door_y - MARGIN / 4, door_w, door_y,
                  0, door_y, door_l_col)
        pyxel.rect(0, door_y, door_w, door_h, door_l_col)
        pyxel.tri(0, door_y + door_h, door_w, door_y + door_h,
                  0, SCORE_BOARD_LINE, door_l_col)

        # 右壁
        right_end = pyxel.width
        pyxel.tri(right_end, CELL_SIZE, right_end - wall_width, deps,
                  right_end, deps, pyxel.COLOR_LIME)
        pyxel.rect(right_end - wall_width, deps,
                   right_end, wall_height, pyxel.COLOR_LIME)
        pyxel.tri(right_end, wall_height + deps,
                  right_end - wall_width, wall_height + deps,
                  right_end, SCORE_BOARD_LINE, pyxel.COLOR_LIME)
        # 右出入口
        door_r_col = pyxel.COLOR_NAVY
        if self.right_door is False:
            door_r_col = pyxel.COLOR_GREEN
        pyxel.tri(right_end, door_y - MARGIN / 4,
                  right_end - door_w, door_y,
                  right_end, door_y, door_r_col)
        pyxel.rect(right_end - door_w, door_y,
                   right_end, door_h, door_r_col)
        pyxel.tri(right_end - door_w, door_y + door_h,
                  right_end, door_y + door_h,
                  right_end, SCORE_BOARD_LINE, door_r_col)

    def DrawScoreBoard(self):
        '''
        スコアボード 描画
        '''
        # 枠
        pyxel.rect(0, SCORE_BOARD_LINE, pyxel.width, CELL_SIZE * 2,
                   pyxel.COLOR_BLACK)
        pyxel.rectb(0, SCORE_BOARD_LINE, pyxel.width, CELL_SIZE * 2,
                    pyxel.COLOR_GRAY)

        y = pyxel.height - 13
        # スコア
        score = self.score + self.score_count
        pyxel.text(3, y, f'score:{score:04}',
                   pyxel.COLOR_WHITE, self.fnt_jp_10)
        # タイトル
        self.DrawMsgCenter('cat fall', y, pyxel.COLOR_WHITE)

        # 疲れ
        fatigue = int(self.player.wait / 10)
        msg = f'fatigue:{fatigue:03}'
        msg_width = self.fnt_jp_10.text_width(msg)
        pyxel.text(pyxel.width - (msg_width + 3), y, msg,
                   pyxel.COLOR_WHITE, self.fnt_jp_10)

    def DrawPlayer(self):
        '''
        プレイヤー描画
        '''
        pyxel.blt(self.player.x, self.player.y, 1, 0, 0,
                  CELL_SIZE * self.player.direction, CELL_SIZE,
                  colkey=pyxel.COLOR_GRAY)

    def DrawEnemy(self):
        '''
        敵描画
        '''
        pyxel.blt(self.ufo.x, self.ufo.y, 2, 0, 0, 32, 16,
                  colkey=pyxel.COLOR_GRAY)
        for e in self.enemies:
            pyxel.blt(e.x, e.y, 1, 0, 0, CELL_SIZE, CELL_SIZE,
                      colkey=pyxel.COLOR_GRAY)

    def DrawSwipe(self):
        '''
        切り替え描画
        '''
        pyxel.rect(0, SCORE_BOARD_LINE - self.swipe,
                   pyxel.width, self.swipe, 0)
        pyxel.rect(0, 0,
                   pyxel.width, self.swipe, 0)

    def DrawGameOver(self):
        '''
        ゲームオーバー描画
        '''
        self.DrawMsgCenter('Game Over', CELL_SIZE,
                           pyxel.COLOR_RED)


# 処理実行
random.seed()
App()
