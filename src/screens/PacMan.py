from .Maze import Maze
from src.models.dataclasses import MlxContext
from src.models import Direction
from src.screens.draw_utils import FrameBuffer

from typing import List
from os import walk
from numpy.typing import NDArray
import numpy as np


_W, _A, _S, _D = 119, 97, 115, 100

_DIRETCIONS = {
    _W: Direction.UP,
    _A: Direction.LEFT,
    _S: Direction.DOWN,
    _D: Direction.RIGHT
}

_UP_FOLDER = "assets/pac_man/pacman-up"
_RIGHT_FOLDER = "assets/pac_man/pacman-right"
_DOWN_FOLDER = "assets/pac_man/pacman-down"
_LEFT_FOLDER = "assets/pac_man/pacman-left"

_NO_COLOR = (0, 0, 0, 0)
_YELLOW = (0, 236, 255, 255)
_BLACK = (0, 0, 0, 255)


class PacMan:
    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze) -> None:
        self._cell_size = cell_size
        pac_size = int(self._cell_size * 0.65)
        self._offset = int(cell_size * 0.2)
        self._fb = FrameBuffer(mlx_ctx, pac_size, pac_size)
        self._maze = maze
        self._pac_x = 0.0
        self._pac_y = 0.0
        self._speed = cell_size * 2.5
        self._direction = Direction.RIGHT
        self._pending_direction = Direction.RIGHT
        self._animation = 0

        self._assets = {
            Direction.UP: self._load_assets(pac_size, _UP_FOLDER),
            Direction.RIGHT: self._load_assets(pac_size, _RIGHT_FOLDER),
            Direction.DOWN: self._load_assets(pac_size, _DOWN_FOLDER),
            Direction.LEFT: self._load_assets(pac_size, _LEFT_FOLDER)
        }

    def get_img_ptr(self) -> int:
        return self._fb.img_ptr

    def update(self, delta_time: float, keycode: int):
        self._move_pac_man(keycode, delta_time)

    def render(self):
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

        self._pac_x, self._pac_y = next_pac_x, next_pac_y

    def _try_turn(self, delta_time: float):
        is_vertical = self._pending_direction in (Direction.UP, Direction.DOWN)
        was_vertical = self._direction in (Direction.UP, Direction.DOWN)

        if is_vertical == was_vertical:
            self._direction = self._pending_direction
            return
        
        if self._check_for_wall(*self._get_next_step_xy(delta_time),
                                self._pending_direction):
            return

        aligned_coord = self._pac_x if is_vertical else self._pac_y
        remainder = aligned_coord % self._cell_size
        tolerance = max(self._speed * delta_time, 1.0)

        if remainder <= tolerance:
            snapped = aligned_coord - remainder
        elif self._cell_size - remainder <= tolerance:
            snapped = aligned_coord - remainder + self._cell_size
        else:
            return

        if is_vertical:
            self._pac_x = snapped
        else:
            self._pac_y = snapped

        self._direction = self._pending_direction

    def _check_for_wall(self, next_x, next_y, direction) -> bool:
        if self._direction in (Direction.UP, Direction.LEFT):
            cell_x = int(np.ceil(next_x / self._cell_size))
            cell_y = int(np.ceil(next_y / self._cell_size))
        else:
            cell_x = int(next_x // self._cell_size)
            cell_y = int(next_y // self._cell_size)

        cell_idx = cell_y * self._maze.width + cell_x

        return self._maze.is_wall_direction(cell_idx, direction)

    def _get_next_step_xy(self, delta_time: float):
        if self._direction == Direction.UP:
            return self._pac_x, self._pac_y - (self._speed * delta_time)
        elif self._direction == Direction.DOWN:
            return self._pac_x, self._pac_y + (self._speed * delta_time)
        elif self._direction == Direction.LEFT:
            return self._pac_x - (self._speed * delta_time), self._pac_y
        elif self._direction == Direction.RIGHT:
            return self._pac_x + (self._speed * delta_time), self._pac_y

    def _load_assets(self, pac_size: int,
                     folder_path: str) -> List[NDArray[np.uint8]]:
        gen = walk(folder_path)
        files = [file for *_, file in gen]
        imgs: List[NDArray[np.uint8]] = []
        for file in files[0]:
            img = self._fb.get_image_array(f"{folder_path}/{file}",
                                           pac_size, pac_size)
            no_color_img = self._fb.swap_colors_in_image_leave_out(
                _YELLOW, _NO_COLOR, img)
            imgs.append(no_color_img)
        return imgs
