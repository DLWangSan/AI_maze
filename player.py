import pygame as pg
from settings import Settings


class Player(pg.sprite.Sprite):
    def __init__(self, color, x, y, radius, w, h):
        # 调用父类Sprite构造函数
        super().__init__()

        # 起始点
        self.start_x = x
        self.start_y = y
        self.settings = Settings(w, h)

        # 创建矩形图像，填充并将背景设置为透明
        self.image = pg.Surface([radius * 2, radius * 2])
        self.image.fill(self.settings.MAZE_COLOR)
        self.image.set_colorkey(self.settings.MAZE_COLOR)

        # 在透明矩形上绘制圆形玩家
        pg.draw.circle(self.image, color, (radius, radius), radius)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    # 归位
    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y

#
# if __name__ == '__main__':
#     play = Player((255,255,255), 0, 0, 5)
