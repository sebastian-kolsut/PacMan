from mazegenerator import MazeGenerator  # type: ignore[import-untyped]
from src.models import Config
from src.models import Direction
from dataclasses import dataclass
from typing import Set


_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3


@dataclass
class Bitboards:
    up: int = 0
    right: int = 0
    down: int = 0
    left: int = 0


class Maze:
    def __init__(self, config: Config):
        self.config = config
        self.level = 0
        self.bitboards = Bitboards()
        self.dirty = False

        self.generate_new_maze()
        self.patters_positions = self._load_42_patern_positions()

    def generate_new_maze(self):
        self.width = self.config.levels[self.level].width
        self.height = self.config.levels[self.level].height
        mazegen = MazeGenerator((self.width, self.height))

        self._reset_bitboard()

        for y in range(self.height):
            for x in range(self.width):
                self._set_cell_value(x, y, mazegen, self.width)

        self.dirty = False

    def is_wall_up(self, bit_idx: int) -> bool:
        return (self.bitboards.up & (1 << bit_idx)) != 0

    def is_wall_right(self, bit_idx: int) -> bool:
        return (self.bitboards.right & (1 << bit_idx)) != 0

    def is_wall_down(self, bit_idx: int) -> bool:
        return (self.bitboards.down & (1 << bit_idx)) != 0

    def is_wall_left(self, bit_idx: int) -> bool:
        return (self.bitboards.left & (1 << bit_idx)) != 0

    def is_wall_direction(self, bit_idx: int, direction: Direction) -> bool:
        match direction:
            case Direction.UP:
                return self.is_wall_up(bit_idx)
            case Direction.RIGHT:
                return self.is_wall_right(bit_idx)
            case Direction.DOWN:
                return self.is_wall_down(bit_idx)
            case Direction.LEFT:
                return self.is_wall_left(bit_idx)

        return False

    def _load_42_patern_positions(self) -> Set[int]:
        positions: Set[int] = set()

        for idx in range(self.width * self.height):
            if self.is_wall_up(idx) and self.is_wall_right(idx) \
                    and self.is_wall_down(idx) and self.is_wall_left(idx):
                positions.add(idx)

        return positions

    def _set_cell_value(self, x: int, y: int, mazegen: MazeGenerator,
                        width: int) -> None:
        bit_pos = y * width + x

        if (mazegen.maze[y][x] & (1 << Direction.UP)) != 0:
            self.bitboards.up |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << Direction.RIGHT)) != 0:
            self.bitboards.right |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << Direction.DOWN)) != 0:
            self.bitboards.down |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << Direction.LEFT)) != 0:
            self.bitboards.left |= (1 << bit_pos)

    def _reset_bitboard(self) -> None:
        self.bitboards.up = 0
        self.bitboards.right = 0
        self.bitboards.down = 0
        self.bitboards.left = 0
