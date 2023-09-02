class Settings:
    def __init__(self, w, h):
        self.name = "PyMaze For A-level Computer Science"

        self.SCREEN_WIDTH = 1300
        self.SCREEN_HEIGHT = 800
        self.MAZE_WIDTH = w  # 方格数
        self.MAZE_HEIGHT = h  #
        self.CELL_COUNT = self.MAZE_WIDTH * self.MAZE_HEIGHT  # 总单元格数
        self.BLOCK_SIZE = 8  # 墙厚
        self.PATH_WIDTH = 3  # 道路宽度
        self.ROUNDS = 10

        # 是否显示迷宫生成过程
        self.SHOW_DRAW = True

        # 墙壁
        self.CELL_SIZE = self.BLOCK_SIZE * self.PATH_WIDTH + self.BLOCK_SIZE  # 右下边缘
        self.MAZE_WIDTH_PX = self.CELL_SIZE * self.MAZE_WIDTH + self.BLOCK_SIZE  # 左边缘
        self.MAZE_HEIGHT_PX = self.CELL_SIZE * self.MAZE_HEIGHT + self.BLOCK_SIZE  # 上边缘

        # 颜色
        self.BACK_COLOR = (100, 100, 100)
        self.WALL_COLOR = (18, 94, 32)
        self.MAZE_COLOR = (255, 255, 255)
        self.UNVISITED_COLOR = (0, 0, 0)
        self.PLAYER1_COLOR = (255, 0, 0)
        self.PLAYER2_COLOR = (0, 0, 255)
        self.MESSAGE_COLOR = (0, 255, 0)
        self.OVER_COLOR = (255, 0, 0)
        self.AI_PATH_COLOR = (0, 255, 0)

        self.smart_ai1_time_delay = 50
        self.smart_ai2_time_delay = 300
        self.smart_ai3_time_delay = 100

        self.MAZE_TOP_LEFT_CORNER = (self.SCREEN_WIDTH // 2 - self.MAZE_WIDTH_PX // 2, self.SCREEN_HEIGHT // 2 - self.MAZE_HEIGHT_PX // 2)

