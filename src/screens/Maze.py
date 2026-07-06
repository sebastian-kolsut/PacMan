from mazegenerator import MazeGenerator  # type: ignore[import-untyped]
from src.models import Config
from dataclasses import dataclass


_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3


@dataclass
class Bitboard:
    up: int = 0
    right: int = 0
    down: int = 0
    left: int = 0


class Maze:
    def __init__(self, config: Config):
        self.config = config
        self.level = 0
        self.bitboard = Bitboard()

        self.generate_new_maze()

    def generate_new_maze(self):
        self.width = self.config.levels[self.level].width
        self.height = self.config.levels[self.level].height
        mazegen = MazeGenerator((self.width, self.height))

        self._reset_bitboard()

        for y in range(self.height):
            for x in range(self.width):
                self._set_cell_value(x, y, mazegen, self.width)

    def is_wall_up(self, bit_idx: int) -> bool:
        return (self.bitboard.up & (1 << bit_idx)) != 0

    def is_wall_right(self, bit_idx: int) -> bool:
        return (self.bitboard.right & (1 << bit_idx)) != 0

    def is_wall_down(self, bit_idx: int) -> bool:
        return (self.bitboard.down & (1 << bit_idx)) != 0

    def is_wall_left(self, bit_idx: int) -> bool:
        return (self.bitboard.left & (1 << bit_idx)) != 0

    def _set_cell_value(self, x: int, y: int, mazegen: MazeGenerator,
                        width: int) -> None:
        bit_pos = y * width + x

        if (mazegen.maze[y][x] & (1 << _UP)) != 0:
            self.bitboard.up |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << _RIGHT)) != 0:
            self.bitboard.right |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << _DOWN)) != 0:
            self.bitboard.down |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << _LEFT)) != 0:
            self.bitboard.left |= (1 << bit_pos)

    def _reset_bitboard(self) -> None:
        self.bitboard.up = 0
        self.bitboard.right = 0
        self.bitboard.down = 0
        self.bitboard.left = 0
