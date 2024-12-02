import pyxel
from values import (WINDOW_WIDTH,
                    WINDOW_HEIGHT,
                    FPS,
                    GamePlay,
                    CELL_SIZE,
                    MARGIN,
                    SCORE_BOARD_LINE,
                    CLOSE,
                    OPEN,
                    ONE_PLAY_SCORE,
                    GameObject)
from player import Player
from enemy import EnemyManager
from item import ItemMagager


# ウインドウ設定
TITLE = 'AlienFall'
DOOR_CYCLE = 180


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title=TITLE, fps=FPS)
        self.variables_init()
        pyxel.run(self.update, self.draw)

    def variables_init(self):
        '''
        内部変数初期化
        '''
        pyxel.mouse(False)
        # リソース読込み
        pyxel.images[0].load(0, 0, 'assets/Pallet.png', incl_colors=True)
        pyxel.images[1].load(0, 0, 'assets/player.png')
        pyxel.images[2].load(0, 0, 'assets/ufo.png')
        self.fnt_jp_10 = pyxel.Font("assets/umplus_j10r.bdf")
        # 内部
        self.game_satate = GamePlay.Title
        self.player = Player(1)
        self.enemies = EnemyManager(2)
        self.items = ItemMagager(1)
        self.button_release = False         # ボタン離したフラグ
        self.game_wait = 0                  # ゲームの汎用ウエイト値
        self.right_door = OPEN              # ドア開閉
        self.score = 0                      # スコア
        self.score_count = 0                # スコア加算時のアニメーション用
        self.door_cyc = DOOR_CYCLE          # ドア閉サイクル
        self.door_close_cnt = 0             # ドア閉時間
        self.ed_ptn = 0
        self.e_val_a = 0

    def update(self):
        '''
        データ更新
        '''
        if self.game_satate == GamePlay.Title:
            if self.InputMainKey():
                self.items.update(self.game_satate)
                self.game_satate = GamePlay.Play

        elif self.game_satate == GamePlay.Play:
            # 画面一時停止
            if self.InputPoseKey():
                self.game_satate = GamePlay.Pose
                return

            # 操作反映
            s = self.player.update(self.game_satate, self.right_door)
            self.enemies.update(self.game_satate, self.score)
            if ONE_PLAY_SCORE <= s:
                self.button_release = False
                self.game_satate = GamePlay.PlayStop
            # 当たり判定
            for e in self.enemies.items:
                if self.isHit(e):
                    self.game_satate = GamePlay.GameOverPre
                    self.game_wait = 240  # 暗転時間セット
                    self.ed_ptn = e.type
            for i in self.items.items:
                if self.isHit(i):
                    # アイテム取得
                    self.player.AddFatigue()
                    i.is_get = True
            self.items.update(self.game_satate)
            # ドア開閉
            self.DoorUpdate()

        elif self.game_satate == GamePlay.Pose:
            # ポーズ解除
            if self.InputPoseKey():
                self.game_satate = GamePlay.Play

        elif self.game_satate == GamePlay.PlayStop:
            # 得点増加演出
            self.score_count += 1
            count = ONE_PLAY_SCORE * self.player.FatiguePoint()
            if count <= self.score_count:
                self.score += count
                self.score_count = 0
                self.player.ResetPos()
                self.items.Reset()
                self.game_satate = GamePlay.PlayReset
            if pyxel.btnr(pyxel.KEY_RIGHT) \
                    or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                self.button_release = True

        elif self.game_satate == GamePlay.PlayReset:
            # 右キー押しっぱなしだと勢いですぐドアから出るので調整
            if pyxel.btnr(pyxel.KEY_RIGHT) \
                    or pyxel.btnr(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) \
                    or self.button_release:
                self.items.update(self.game_satate)
                self.game_satate = GamePlay.Play

        elif self.game_satate == GamePlay.GameOverPre:
            # 暗転処理用
            self.game_wait -= 1
            if self.game_wait <= 0:
                self.game_satate = GamePlay.GameOver

        elif self.game_satate == GamePlay.GameOver:
            # リセットして再開
            if self.InputMainKey():
                self.player.ResetPos()
                self.enemies.Reset()
                self.items.Reset()
                self.score = 0
                self.items.update(self.game_satate)
                self.game_satate = GamePlay.Play
            if self.ed_ptn == 1:
                self.e_val_a += 1
                if 60 < self.e_val_a:
                    # ふよふよ
                    # self.e_val_a = -60
                    # 対峙
                    self.e_val_a = 60

    def draw(self):
        '''
        描画更新
        '''
        if self.game_satate != GamePlay.GameOver:
            # ゲームオーバー時以外の共通描画
            pyxel.cls(pyxel.COLOR_LIGHT_BLUE)
            self.DrawBackground()
            self.player.draw()
            self.enemies.draw()
            self.items.draw()

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
            self.DrawMsgCenter('Game Over', CELL_SIZE,
                               pyxel.COLOR_RED)
            self.EDMovie()

        self.DrawScoreBoard()

    def InputMainKey(self):
        if pyxel.btnp(pyxel.KEY_SPACE) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
            return True
        return False
    
    def InputPoseKey(self):
        if pyxel.btnp(pyxel.KEY_P) \
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            return True
        return False

    def isHit(self, obj: GameObject):
        '''
        当たり判定
        obj -> enemy or item
        '''
        l1 = self.player.x
        t1 = self.player.y
        r1 = self.player.x + CELL_SIZE
        b1 = self.player.y + CELL_SIZE

        l2 = obj.pos.x
        t2 = obj.pos.y
        r2 = obj.pos.x + obj.w
        b2 = obj.pos.y + obj.h

        if r2 > l1 and r1 > l2 \
                and b2 > t1 and b1 > t2:
            return True  # ヒット
        return False  # ヒットなし

    def DoorUpdate(self):
        '''
        ドア開閉更新
        '''
        if self.right_door is CLOSE:
            self.door_close_cnt -= 1
            if self.door_close_cnt <= 0:
                self.right_door = OPEN
                self.door_cyc = DOOR_CYCLE
        else:
            self.door_cyc -= 1
            if self.door_cyc <= 0:
                r = pyxel.rndi(0, 100)
                if r < 20:  # ２０％の確率で閉まる
                    self.right_door = CLOSE
                    # ２～６秒間閉まる
                    self.door_close_cnt = pyxel.rndi(2, 6) * FPS

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
        # 左壁
        wall_width = CELL_SIZE * 2
        deps = CELL_SIZE * 2
        wall_height = SCORE_BOARD_LINE - deps - CELL_SIZE
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
        self.DrawMsgCenter(TITLE, y, pyxel.COLOR_WHITE)

        # 疲れ
        x = pyxel.width - 55
        pyxel.text(x, y - 12, 'Weight',
                   pyxel.COLOR_WHITE, self.fnt_jp_10)
        pyxel.rectb(x, y, 50, 10, pyxel.COLOR_WHITE)
        w = min(50, self.player.fatigue * 10)
        pyxel.rect(x, y, w, 10, pyxel.COLOR_WHITE)

    def DrawSwipe(self):
        '''
        切り替え描画
        '''
        pyxel.rect(0, self.game_wait,
                   pyxel.width, SCORE_BOARD_LINE - self.game_wait, 0)
        pyxel.rect(0, 0,
                   pyxel.width, SCORE_BOARD_LINE - self.game_wait, 0)

    def EDMovie(self):
        '''
        ED
        '''
        if self.ed_ptn == 1:
            white = pyxel.COLOR_WHITE
            # ふよふよ
            # y = self.fuyofuyo()
            # pyxel.elli(pyxel.width / 2, y, 10, 10, pyxel.COLOR_WHITE)
            # 対峙
            x = self.e_val_a / 2
            pyxel.rect(x, SCORE_BOARD_LINE - 130, 100, 130, white)
            pyxel.rect(pyxel.width - x - 100, SCORE_BOARD_LINE - 170, 100, 150, white)
        elif self.ed_ptn == 2:
            pass

    def fuyofuyo(self):
        return (self.e_val_a * self.e_val_a) / 120 + (pyxel.height / 2)


App()
