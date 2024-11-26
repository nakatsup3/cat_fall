import pyxel
from values import (CELL_SIZE,
                    MARGIN,
                    PLAY_BOTTOM_LINE,
                    GamePlay,
                    GameObject)


class Item(GameObject):
    def __init__(self):
        super().__init__()
        self.h = 8
        self.w = 8
        self.is_get = False


class ItemMagager:
    def __init__(self, img_idx):
        self.img_idx = img_idx
        self.items = []

    def update(self, game_state: GamePlay):
        if game_state == GamePlay.Title \
                or game_state == GamePlay.PlayReset \
                or game_state == GamePlay.GameOver:
            # アイテム生成
            cnt = pyxel.rndi(0, 6)
            for i in range(cnt):
                itm = Item()
                itm.pos.x = pyxel.rndi(MARGIN, pyxel.width - MARGIN - itm.w)
                itm.pos.y = PLAY_BOTTOM_LINE - CELL_SIZE - itm.h
                self.items.append(itm)

        if game_state == GamePlay.Play:
            # 取得済みアイテム消去
            tmp = []
            while self.items:
                i = self.items.pop()
                if i.is_get is False:
                    tmp.append(i)
            while tmp:
                self.items.append(tmp.pop())

    def draw(self):
        for i in self.items:
            pyxel.elli(i.pos.x, i.pos.y, i.w, i.h, pyxel.COLOR_YELLOW)

    def Reset(self):
        self.items.clear()
