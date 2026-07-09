from .Maze import Maze
from src.models.dataclasses import MlxContext
from src.models import Direction
from .Character import Character

from numpy.typing import NDArray
import numpy as np


_W, _A, _S, _D = 119, 97, 115, 100
_A_UP, _A_RIGHT, _A_DOWN, _A_LEFT = 65362, 65363, 65364, 65361

_DIRETCIONS = {
    _W: Direction.UP,
    _A: Direction.LEFT,
    _S: Direction.DOWN,
    _D: Direction.RIGHT,
    _A_UP: Direction.UP,
    _A_LEFT: Direction.LEFT,
    _A_DOWN: Direction.DOWN,
    _A_RIGHT: Direction.RIGHT
}

_UP_FOLDER = "assets/pac_man/pacman-up"
_RIGHT_FOLDER = "assets/pac_man/pacman-right"
_DOWN_FOLDER = "assets/pac_man/pacman-down"
_LEFT_FOLDER = "assets/pac_man/pacman-left"


class PacMan(Character):
    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze) -> None:
        super().__init__(cell_size, mlx_ctx, maze)
        self._animation = 0

        self._assets = {
            Direction.UP: self._load_assets(self._character_size, _UP_FOLDER),
            Direction.RIGHT: self._load_assets(self._character_size,
                                               _RIGHT_FOLDER),
            Direction.DOWN: self._load_assets(self._character_size,
                                              _DOWN_FOLDER),
            Direction.LEFT: self._load_assets(self._character_size,
                                              _LEFT_FOLDER)
        }

    def update(self, delta_time: float, keycode: int):
        self._move_pac_man(keycode, delta_time)

    def render(self) -> NDArray[np.uint8]:
        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]
        self._fb.draw_blended_tile(
            pixels,
            self._assets[self._direction][self._animation // 3], 0, 0)
        self._animation += 1
        if self._animation == 9:
            self._animation = 0

        return pixels

    def _move_pac_man(self, keycode: int, delta_time: float):
        if keycode != 0:
            self._pending_direction = _DIRETCIONS[keycode]
        self._try_turn(delta_time)

        next_pac_x, next_pac_y = self._get_next_step_xy(delta_time)

        if self._check_for_wall(next_pac_x, next_pac_y, self._direction):
            dir = self._direction
            pen = self._pending_direction
            self._pending_direction = Direction.UP
            self._try_turn(delta_time)
            self._pending_direction = Direction.RIGHT
            self._try_turn(delta_time)
            self._direction = dir
            self._pending_direction = pen
            return

        self._pos_x, self._pos_y = next_pac_x, next_pac_y
