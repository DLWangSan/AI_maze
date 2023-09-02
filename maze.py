import heapq
import random
from collections import deque
from queue import Queue

import pygame as pg

from player import Player
from settings import Settings
from utils import CellProp, Direction


class MazeGenerator:
    direction_to_flag = {
        Direction.North: CellProp.Path_N,
        Direction.East: CellProp.Path_E,
        Direction.South: CellProp.Path_S,
        Direction.West: CellProp.Path_W
    }

    opposite_direction = {
        Direction.North: Direction.South,
        Direction.East: Direction.West,
        Direction.South: Direction.North,
        Direction.West: Direction.East
    }

    def __init__(self, w, h):
        pg.init()
        self.settings = Settings(w, h)
        self.screen = pg.display.set_mode((self.settings.SCREEN_WIDTH, self.settings.SCREEN_HEIGHT))

        pg.display.set_caption(self.settings.name)
        # 用列表存放二维数组
        self.maze = []
        self.maze_image = None

        # 创建玩家
        self.player1 = Player(self.settings.PLAYER1_COLOR,
                              self.settings.MAZE_TOP_LEFT_CORNER[0] + self.settings.BLOCK_SIZE,
                              self.settings.MAZE_TOP_LEFT_CORNER[1] + self.settings.BLOCK_SIZE,
                              (self.settings.BLOCK_SIZE * 3) // 2,
                              self.settings.MAZE_WIDTH,
                              self.settings.MAZE_HEIGHT)
        self.player1_sprite = None

        self.player2 = Player(self.settings.PLAYER2_COLOR,
                              self.settings.MAZE_TOP_LEFT_CORNER[0] + self.settings.MAZE_WIDTH_PX - self.settings.CELL_SIZE,
                              self.settings.MAZE_TOP_LEFT_CORNER[1] + self.settings.MAZE_HEIGHT_PX - self.settings.CELL_SIZE,
                              (self.settings.BLOCK_SIZE * 3) // 2,
                              self.settings.MAZE_WIDTH,
                              self.settings.MAZE_HEIGHT
                              )
        self.player2_sprite = None

        # 获胜判断
        self.win1_flag = False
        self.win2_flag = False

        self.inc_x = self.settings.BLOCK_SIZE * 2
        self.inc_y = self.settings.BLOCK_SIZE * 2

        self.player_1_left_keeping = False
        self.player_1_right_keeping = False
        self.player_1_up_keeping = False
        self.player_1_down_keeping = False
        self.player_2_left_keeping = False
        self.player_2_right_keeping = False
        self.player_2_up_keeping = False
        self.player_2_down_keeping = False

        self.last_ai_move_time = 0
        self.ai_move_delay_1 = self.settings.smart_ai1_time_delay
        self.ai_move_delay_2 = self.settings.smart_ai2_time_delay
        self.ai_move_delay_3 = self.settings.smart_ai3_time_delay

        self.all = self.settings.ROUNDS
        self.now = 1

        self.player1_score = 0
        self.player2_score = 0

        self.rule_player2 = 0
        self.ruling_color = (0, 255, 0)


    # 获取单元格索引
    def get_cell_index(self, position):
        x, y = position
        return y * self.settings.MAZE_WIDTH + x

    def generate_maze(self):

        self.maze = [0] * self.settings.CELL_COUNT
        visited_count = 0

        # 将第一个单元格 （0，0） 添加到堆栈并增加访问计数
        process_stack = [(0, 0)]
        self.maze[0] |= CellProp.Visited.value

        visited_count += 1

        # 循环访问相邻格子
        while visited_count < self.settings.CELL_COUNT:
            x, y = process_stack[-1]  # 获取栈顶坐标
            current_cell_index = self.get_cell_index((x, y))

            # 找出所有未访问相邻格，遍历枚举
            # 创建未访问相邻格列表
            neighbors = []
            for direction in Direction:
                dir = direction.value
                new_x, new_y = (x + dir[0], y + dir[1])
                if 0 <= new_x < self.settings.MAZE_WIDTH and 0 <= new_y < self.settings.MAZE_HEIGHT:
                    index = self.get_cell_index((new_x, new_y))
                    # 若未访问过
                    if not self.maze[index] & CellProp.Visited.value:
                        neighbors.append((new_x, new_y, direction))
            # 检查未访问相邻格
            if len(neighbors) > 0:
                # 随机选择邻格
                cell = neighbors[random.randrange(len(neighbors))]
                cell_x, cell_y, cell_direction = cell
                cell_position = (cell_x, cell_y)
                cell_index = self.get_cell_index(cell_position)

                # 用相连接的方向状态开辟路径
                flag_to = MazeGenerator.direction_to_flag[cell_direction]
                flag_from = MazeGenerator.direction_to_flag[MazeGenerator.opposite_direction[cell_direction]]

                self.maze[current_cell_index] |= flag_to.value
                self.maze[cell_index] |= flag_from.value | CellProp.Visited.value

                process_stack.append(cell_position)
                visited_count += 1
            else:
                # 回溯未访问的格子
                process_stack.pop()
            if self.settings.SHOW_DRAW:
                self.draw_maze()
                pg.display.update()
                pg.event.pump()

        # self.draw_maze()
        pg.display.update()
        self.maze_image = self.screen.copy()

    def draw(self, color, x, y):
        x_offset = self.settings.MAZE_TOP_LEFT_CORNER[0] + self.settings.BLOCK_SIZE
        y_offset = self.settings.MAZE_TOP_LEFT_CORNER[1] + self.settings.BLOCK_SIZE
        pg.draw.rect(self.screen, color, (x * self.settings.BLOCK_SIZE + x_offset,
                                          y * self.settings.BLOCK_SIZE + y_offset,
                                          self.settings.BLOCK_SIZE, self.settings.BLOCK_SIZE))

    def draw_maze(self):

        if self.now == self.all + 1:
            return

        self.screen.fill(self.settings.BACK_COLOR)
        # 底色（墙）
        pg.draw.rect(self.screen, self.settings.WALL_COLOR, (self.settings.MAZE_TOP_LEFT_CORNER[0],
                                                             self.settings.MAZE_TOP_LEFT_CORNER[1],
                                                             self.settings.MAZE_WIDTH_PX,
                                                             self.settings.MAZE_HEIGHT_PX))
        # 循环迷宫列表
        for x in range(self.settings.MAZE_WIDTH):
            for y in range(self.settings.MAZE_HEIGHT):
                for py in range(self.settings.PATH_WIDTH):
                    for px in range(self.settings.PATH_WIDTH):
                        cell_index = self.get_cell_index((x, y))
                        if self.maze[cell_index] & CellProp.Visited.value:
                            self.draw(self.settings.MAZE_COLOR, x *
                                      (self.settings.PATH_WIDTH + 1) + px, y * (self.settings.PATH_WIDTH + 1) + py)
                        else:
                            self.draw(self.settings.UNVISITED_COLOR, x * (self.settings.PATH_WIDTH + 1) + px,
                                      y * (self.settings.PATH_WIDTH + 1) + py)

                # 检查是否有连接的路径，打通墙壁
                for p in range(self.settings.PATH_WIDTH):
                    if self.maze[y * self.settings.MAZE_WIDTH + x] & CellProp.Path_S.value:
                        self.draw(self.settings.MAZE_COLOR, x * (self.settings.PATH_WIDTH + 1) + p,
                                  y * (self.settings.PATH_WIDTH + 1) + self.settings.PATH_WIDTH)

                    if self.maze[y * self.settings.MAZE_WIDTH + x] & CellProp.Path_E.value:
                        self.draw(self.settings.MAZE_COLOR,
                                  x * (self.settings.PATH_WIDTH + 1) + self.settings.PATH_WIDTH,
                                  y * (self.settings.PATH_WIDTH + 1) + p)
        # 迷宫出口
        pg.draw.rect(self.screen, self.settings.PLAYER2_COLOR, (self.settings.MAZE_TOP_LEFT_CORNER[0],
                                                                self.settings.MAZE_TOP_LEFT_CORNER[
                                                                    1] + self.settings.BLOCK_SIZE,
                                                                self.settings.BLOCK_SIZE, self.settings.BLOCK_SIZE * 3))

        pg.draw.rect(self.screen, self.settings.PLAYER1_COLOR,
                     (self.settings.MAZE_TOP_LEFT_CORNER[0] + self.settings.MAZE_WIDTH_PX - self.settings.BLOCK_SIZE,
                      self.settings.MAZE_TOP_LEFT_CORNER[
                          1] + self.settings.MAZE_HEIGHT_PX - self.settings.BLOCK_SIZE * 4,
                      self.settings.BLOCK_SIZE, self.settings.BLOCK_SIZE * 3))

    def draw_screen(self):
        # self.draw_maze()
        self.screen.blit(self.maze_image, (0, 0))
        self.player1_sprite.draw(self.screen)
        self.player2_sprite.draw(self.screen)

        # 绘制关数
        now = self.now if self.now <= self.all else self.all
        font = pg.font.SysFont(None, 24)
        pg.draw.rect(self.screen, (0,255,255), (10, 10, 200, 30))
        per_text = font.render(f"Round {now} / {self.all}", True, pg.Color('black'))
        self.screen.blit(per_text, (55, 17))

        # 绘制 Player 2 按钮
        if self.rule_player2 == 0:
            pg.draw.rect(self.screen, self.ruling_color, (self.settings.SCREEN_WIDTH - 270, 60, 60, 50), border_radius=2)
        elif self.rule_player2 == 1:
            pg.draw.rect(self.screen, self.ruling_color, (self.settings.SCREEN_WIDTH - 210, 60, 60, 50), border_radius=2)
        elif self.rule_player2 == 2:
            pg.draw.rect(self.screen, self.ruling_color, (self.settings.SCREEN_WIDTH - 150, 60, 60, 50), border_radius=2)
        elif self.rule_player2 == 3:
            pg.draw.rect(self.screen, self.ruling_color, (self.settings.SCREEN_WIDTH - 90, 60, 60, 50), border_radius=2)

        font = pg.font.SysFont(None, 28)
        pg.draw.rect(self.screen, (255,255,255), (self.settings.SCREEN_WIDTH-270, 10, 240, 50))
        smart_text = font.render(f"PLAYER 2:   {self.player2_score}", True, pg.Color('blue'))
        self.screen.blit(smart_text, (self.settings.SCREEN_WIDTH-270 + 210//2 - 55 , 25))

        # 真人/AI三等级按钮
        font = pg.font.SysFont(None, 20)
        pg.draw.rect(self.screen, (255, 255, 255), (self.settings.SCREEN_WIDTH - 270, 60, 60, 50), width=2, border_radius=2)
        man_text = font.render("MAN", True, pg.Color('black'))
        self.screen.blit(man_text, (self.settings.SCREEN_WIDTH - 270 + 210 // 4 - 37 , 25+55))

        pg.draw.rect(self.screen, (255, 255, 255), (self.settings.SCREEN_WIDTH - 210, 60, 60, 50), width=2, border_radius=2)
        man_text = font.render("AI 1", True, pg.Color('black'))
        self.screen.blit(man_text, (self.settings.SCREEN_WIDTH - 210 + 210 // 4 - 37, 25 + 55))

        pg.draw.rect(self.screen, (255, 255, 255), (self.settings.SCREEN_WIDTH - 150, 60, 60, 50), width=2, border_radius=2)
        man_text = font.render("AI 2", True, pg.Color('black'))
        self.screen.blit(man_text, (self.settings.SCREEN_WIDTH - 150 + 210 // 4 - 37, 25 + 55))

        pg.draw.rect(self.screen, (255, 255, 255), (self.settings.SCREEN_WIDTH - 90, 60, 60, 50), width=2, border_radius=2)
        man_text = font.render("AI 3", True, pg.Color('black'))
        self.screen.blit(man_text, (self.settings.SCREEN_WIDTH - 90 + 210 // 4 - 37, 25 + 55))

        # 绘制 Player 1 按钮
        font = pg.font.SysFont(None, 30)
        pg.draw.rect(self.screen, (255, 255, 255), (self.settings.SCREEN_WIDTH - 270 -270, 10, 240, 100))
        player1_text = font.render(f"PLAYER 1:   {self.player1_score}", True, pg.Color('red'))
        self.screen.blit(player1_text, (self.settings.SCREEN_WIDTH - 270 - 270 + 210 // 2 - 60, 50))

        pg.display.update()

    def can_move(self, direction, player):
        # 左上角第一格
        corner_offset_x = self.settings.MAZE_TOP_LEFT_CORNER[0] + self.settings.BLOCK_SIZE
        corner_offset_y = self.settings.MAZE_TOP_LEFT_CORNER[1] + self.settings.BLOCK_SIZE

        # 计算玩家占用单元格
        square = self.settings.BLOCK_SIZE * 4
        p1 = (player.rect.x - corner_offset_x, player.rect.y - corner_offset_y)
        p2 = (p1[0] + square - 1, p1[1] + square - 1)
        player_pos1 = (p1[0] // square, p1[1] // square)
        player_pos2 = (p2[0] // square, p2[1] // square)
        cell_index1 = self.get_cell_index((player_pos1[0], player_pos1[1]))
        cell_index2 = self.get_cell_index((player_pos2[0], player_pos2[1]))

        functions = {
            Direction.North: self.can_move_up,
            Direction.East: self.can_move_right,
            Direction.South: self.can_move_down,
            Direction.West: self.can_move_left
        }

        # 检查迷宫出口
        # 检查玩家是否在对方玩家的起点（获胜判断）
        if self.player1.rect.x == self.player2.start_x and self.player1.rect.y == self.player2.start_y:
            self.win1_flag = True
        elif self.player2.rect.x == self.player1.start_x and self.player2.rect.y == self.player1.start_y:
            self.win2_flag = True

        return functions[direction](cell_index1, cell_index2)

    def can_move_up(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_N.value
        else:
            return index2 == index1 + self.settings.MAZE_WIDTH

    def can_move_right(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_E.value
        else:
            return index2 == index1 + 1

    def can_move_down(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_S.value
        else:
            return index2 == index1 + self.settings.MAZE_WIDTH

    def can_move_left(self, index1, index2):
        if index1 == index2:
            return self.maze[index1] & CellProp.Path_W.value
        else:
            return index2 == index1 + 1

    def move_up(self, player):
        if self.can_move(Direction.North, player):
            player.rect.y -= self.inc_y*2

    def move_right(self, player):
        if self.can_move(Direction.East, player):
            player.rect.x += self.inc_x*2

    def move_down(self, player):
        if self.can_move(Direction.South, player):
            player.rect.y += self.inc_y*2

    def move_left(self, player):
        if self.can_move(Direction.West, player):
            player.rect.x -= self.inc_x*2

    # 获胜提示
    def display_win(self):
        msg = f'Player 1 Wins Round {self.now -1}!!!' if self.win1_flag else f'Player 2 Wins Round {self.now-1}!!!'
        if self.win1_flag:
            self.player1_score += 10
        else:
            self.player2_score += 10

        font = pg.font.SysFont('Arial', 72, True)
        size = font.size(msg)
        s = font.render(msg, True, self.settings.MESSAGE_COLOR, (0, 0, 0))
        self.screen.blit(s,
                         (self.settings.SCREEN_WIDTH // 2 - size[0] // 2, self.settings.SCREEN_HEIGHT // 2 - size[1] // 2))
        pg.display.update()
        pg.time.wait(1000)

    def game_over(self):
        if self.player1_score == self.player2_score:
            msg = f"GAME OVER!!!\n Draw!!!"
        else:
            winner = "PLAYER 1" if self.player1_score > self.player2_score else "PLAYER 2"
            msg = f"GAME OVER!!!\n {winner} Wins the WHOLE Game"
        font = pg.font.SysFont('Arial', 36, True)
        size = font.size(msg)
        s = font.render(msg, True, self.settings.OVER_COLOR, (0, 0, 0))
        self.screen.blit(s,
                         (self.settings.SCREEN_WIDTH // 2 - size[0] // 3,
                          self.settings.SCREEN_HEIGHT // 2 - size[1] // 2))

        pg.display.update()
        pg.time.wait(3000)

    def initialize(self):
        self.player1_sprite = None
        self.player1.reset()
        self.player2_sprite = None
        self.player2.reset()

        self.generate_maze()
        self.player1_sprite = pg.sprite.GroupSingle(self.player1)
        self.player2_sprite = pg.sprite.GroupSingle(self.player2)

    def run_game(self):

        fps = pg.time.Clock()
        self.initialize()

        run = True

        start_flag = False
        while run:
            if self.now == self.all + 1:
                self.game_over()
                break
            current_time = pg.time.get_ticks()  # 获取当前时间（毫秒）

            if not self.win1_flag and not self.win2_flag:
                if self.rule_player2 == 1:
                    if start_flag:
                        if current_time - self.last_ai_move_time >= self.ai_move_delay_1:
                            self.ai_move_normal(self.player2)
                            self.last_ai_move_time = current_time  # 更新上次AI移动的时间
                elif self.rule_player2 == 2:
                    if start_flag:
                        # 控制AI移动的间隔
                        if current_time - self.last_ai_move_time >= self.ai_move_delay_2:
                            self.ai_move_smart(self.player2)
                            self.last_ai_move_time = current_time  # 更新上次AI移动的时间
                elif self.rule_player2 == 3:
                    if start_flag:
                        if current_time - self.last_ai_move_time >= self.ai_move_delay_3:
                            self.ai_move_genius(self.player2)
                            self.last_ai_move_time = current_time  # 更新上次AI移动的时间

            else:
                self.now += 1
                self.display_win()
                self.initialize()
                self.win1_flag = self.win2_flag = False
                start_flag = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False

                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        if self.settings.SCREEN_WIDTH-270 <= event.pos[0] < self.settings.SCREEN_WIDTH-270+60\
                                and 60 <= event.pos[1] < 60+50:
                            self.rule_player2 = 0
                        elif self.settings.SCREEN_WIDTH-210 <= event.pos[0] < self.settings.SCREEN_WIDTH-210+60\
                                and 60 <= event.pos[1] < 60+50:
                            self.rule_player2 = 1
                        elif self.settings.SCREEN_WIDTH-150 <= event.pos[0] < self.settings.SCREEN_WIDTH-150+60\
                                and 60 <= event.pos[1] < 60+50:
                            self.rule_player2 = 2
                        elif self.settings.SCREEN_WIDTH-90 <= event.pos[0] < self.settings.SCREEN_WIDTH-90+60\
                                and 60 <= event.pos[1] < 60+50:
                            self.rule_player2 = 3

                elif event.type == pg.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pg.KEYUP:
                    self._check_keyup_events(event)

                if not self.win1_flag and not self.win2_flag:
                    # keys = pg.key.get_pressed()

                    if self.player_1_left_keeping:
                        self.move_left(self.player1)
                        start_flag = True

                    if self.player_1_right_keeping:
                        self.move_right(self.player1)
                        start_flag = True

                    if self.player_1_up_keeping:
                        self.move_up(self.player1)
                        start_flag = True

                    if self.player_1_down_keeping:
                        self.move_down(self.player1)
                        start_flag = True

                    if self.player_2_left_keeping:
                        self.move_left(self.player2)
                        start_flag = True

                    if self.player_2_right_keeping:
                        self.move_right(self.player2)
                        start_flag = True

                    if self.player_2_up_keeping:
                        self.move_up(self.player2)
                        start_flag = True

                    if self.player_2_down_keeping:
                        self.move_down(self.player2)
                        start_flag = True

                    if self.win1_flag or self.win2_flag:
                        self.now += 1
                        self.display_win()
                        self.initialize()
                        self.win1_flag = self.win2_flag = False
                        start_flag = False

            self.draw_screen()
            pg.display.set_caption(f'{self.settings.name} ({str(int(fps.get_fps()))} FPS)')
            fps.tick()


    def _check_keydown_events(self, event):
        if event.key == pg.K_LEFT:
            self.player_2_left_keeping = True
        elif event.key == pg.K_RIGHT:
            self.player_2_right_keeping = True
        elif event.key == pg.K_UP:
            self.player_2_up_keeping = True
        elif event.key == pg.K_DOWN:
            self.player_2_down_keeping = True

        elif event.key == pg.K_a:
            self.player_1_left_keeping = True
        elif event.key == pg.K_d:
            self.player_1_right_keeping = True
        elif event.key == pg.K_w:
            self.player_1_up_keeping = True
        elif event.key == pg.K_s:
            self.player_1_down_keeping = True


    def _check_keyup_events(self, event):
        if event.key == pg.K_LEFT:
            self.player_2_left_keeping = False
        elif event.key == pg.K_RIGHT:
            self.player_2_right_keeping = False
        elif event.key == pg.K_UP:
            self.player_2_up_keeping = False
        elif event.key == pg.K_DOWN:
            self.player_2_down_keeping = False

        elif event.key == pg.K_a:
            self.player_1_left_keeping = False
        elif event.key == pg.K_d:
            self.player_1_right_keeping = False
        elif event.key == pg.K_w:
            self.player_1_up_keeping = False
        elif event.key == pg.K_s:
            self.player_1_down_keeping = False


    def ai_move_normal(self, player):
        directions = [Direction.North, Direction.East, Direction.South, Direction.West]
        valid_directions = [dir for dir in directions if self.can_move(dir, player)]
        if valid_directions:
            selected_direction = random.choice(valid_directions)
            self.move_in_direction(selected_direction, player)

    def ai_move_smart(self, player):
        # start_x = self.settings.MAZE_WIDTH - 1
        start_x = (player.rect.x - self.settings.MAZE_TOP_LEFT_CORNER[0]) // (self.inc_x * 2)
        start_y = (player.rect.y - self.settings.MAZE_TOP_LEFT_CORNER[1]) // (self.inc_y * 2)
        start_index = self.get_cell_index((start_x, start_y))
        # print("start x,y: {}, {}: {}".format(start_x, start_y, start_index))

        target_x = 0
        target_y = 0
        target_index = self.get_cell_index((target_x, target_y))

        path = self.find_shortest_path(start_index, target_index)

        if path:
            if path == [0]:
                self.win2_flag = True
                return
            next_cell = path[1]  # The next cell in the path (excluding current position)
            next_x = next_cell % self.settings.MAZE_WIDTH
            next_y = next_cell // self.settings.MAZE_WIDTH

            ai_x = path[0] % self.settings.MAZE_WIDTH
            ai_y = path[0] // self.settings.MAZE_WIDTH

            if next_x > ai_x:
                self.move_right(player)
            elif next_x < ai_x:
                self.move_left(player)
            elif next_y > ai_y:
                self.move_down(player)
            elif next_y < ai_y:
                self.move_up(player)

    def ai_move_genius(self, player):
        start_x = (player.rect.x - self.settings.MAZE_TOP_LEFT_CORNER[0]) // (self.inc_x * 2)
        start_y = (player.rect.y - self.settings.MAZE_TOP_LEFT_CORNER[1]) // (self.inc_y * 2)
        start_index = self.get_cell_index((start_x, start_y))

        target_x = 0
        target_y = 0
        target_index = self.get_cell_index((target_x, target_y))

        path = self.find_path_astar(start_index, target_index)
        if path:
            if path == [0]:
                self.win2_flag = True
                return
            next_cell = path[1]  # The next cell in the path (excluding current position)
            next_x = next_cell % self.settings.MAZE_WIDTH
            next_y = next_cell // self.settings.MAZE_WIDTH

            ai_x = path[0] % self.settings.MAZE_WIDTH
            ai_y = path[0] // self.settings.MAZE_WIDTH

            if next_x > ai_x:
                self.move_right(player)
            elif next_x < ai_x:
                self.move_left(player)
            elif next_y > ai_y:
                self.move_down(player)
            elif next_y < ai_y:
                self.move_up(player)

    # 使用A*算法寻找从start到end的最短路径
    def find_path_astar(self, start, end):
        open_list = [(0, start)]
        came_from = {}
        g_score = {start: 0}

        while open_list:
            _, current = heapq.heappop(open_list)

            if current == end:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = g_score[neighbor] + self.heuristic(neighbor, end)
                    heapq.heappush(open_list, (f_score, neighbor))

        return []

    def heuristic(self, current, target):
        current_x = current % self.settings.MAZE_WIDTH
        current_y = current // self.settings.MAZE_WIDTH
        target_x = target % self.settings.MAZE_WIDTH
        target_y = target // self.settings.MAZE_WIDTH

        # 使用曼哈顿距离作为启发式估计
        return abs(current_x - target_x) + abs(current_y - target_y)

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.insert(0, current)
        return path

    def get_neighbors(self, index):
        neighbors = []
        x = index % self.settings.MAZE_WIDTH
        y = index // self.settings.MAZE_WIDTH

        for direction in Direction:
            dir_x, dir_y = direction.value
            new_x, new_y = x + dir_x, y + dir_y

            if 0 <= new_x < self.settings.MAZE_WIDTH and 0 <= new_y < self.settings.MAZE_HEIGHT:
                new_index = new_y * self.settings.MAZE_WIDTH + new_x
                if self.is_valid_move(index, new_index):
                    neighbors.append(new_index)

        return neighbors

    def find_shortest_path(self, start, target):
        visited = set()
        queue = Queue()
        queue.put([start])

        while not queue.empty():
            path = queue.get()
            current = path[-1]

            if current == target:
                return path

            if current in visited:
                continue

            visited.add(current)

            neighbors = [current - self.settings.MAZE_WIDTH, current + 1, current + self.settings.MAZE_WIDTH,
                         current - 1]
            for neighbor in neighbors:
                if not self.is_valid_move(current, neighbor):
                    continue

                new_path = list(path)
                new_path.append(neighbor)
                queue.put(new_path)

        return []

    def is_valid_move(self, current, neighbor):
        return 0 <= neighbor < self.settings.CELL_COUNT and \
            self.maze[current] & MazeGenerator.direction_to_flag[self.get_direction(current, neighbor)].value

    def get_direction(self, current, neighbor):
        if neighbor == current - self.settings.MAZE_WIDTH:
            return Direction.North
        elif neighbor == current + 1:
            return Direction.East
        elif neighbor == current + self.settings.MAZE_WIDTH:
            return Direction.South
        elif neighbor == current - 1:
            return Direction.West

    def move_in_direction(self, direction, player):
        if direction == Direction.North:
            self.move_up(player)
        elif direction == Direction.East:
            self.move_right(player)
        elif direction == Direction.South:
            self.move_down(player)
        elif direction == Direction.West:
            self.move_left(player)


