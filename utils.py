# 用枚举表示格子四方向访问状态
from enum import Enum


class CellProp(Enum):
    Path_N = 1
    Path_E = 2
    Path_S = 4
    Path_W = 8
    Visited = 16


class Direction(Enum):
    North = (0, -1)
    East = (1, 0)
    South = (0, 1)
    West = (-1, 0)