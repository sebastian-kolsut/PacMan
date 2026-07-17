from .Maze import Maze
from src.models.dataclasses import MlxContext
from src.models import Direction
from src.screens.draw_utils import FrameBuffer

from typing import List, Tuple
from os import walk
from numpy.typing import NDArray
from abc import ABC, abstractmethod
import numpy as np


class Character(ABC):
    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze) -> None:
        self._cell_size = cell_size
        self._character_size = int(self._cell_size * 0.65)
        self._offset = int(cell_size * 0.2)
        self._fb = FrameBuffer(mlx_ctx, self._character_size,
                               self._character_size)
        self._maze = maze
        self._pos_x = 0.0
        self._pos_y = 0.0
        self._speed = cell_size * 3.0
        self._direction = Direction.RIGHT
        self._pending_direction = Direction.RIGHT

    @abstractmethod
    def render(self) -> NDArray[np.uint8]:
        ...

    def get_img_ptr(self) -> int:
        return self._fb.img_ptr

    def _try_turn(self, delta_time: float):
        is_vertical = self._pending_direction in (Direction.UP, Direction.DOWN)
        was_vertical = self._direction in (Direction.UP, Direction.DOWN)

        if is_vertical == was_vertical:
            self._direction = self._pending_direction
            return

        next_x, next_y = self._get_next_step_xy(delta_time)

        if self._check_for_wall(next_x, next_y, self._pending_direction):
            return

        aligned_coord = self._pos_x if is_vertical else self._pos_y
        remainder = aligned_coord % self._cell_size
        tolerance = max(self._speed * delta_time, 1.0)

        if remainder <= tolerance:
            snapped = aligned_coord - remainder
        elif self._cell_size - remainder <= tolerance:
            snapped = aligned_coord - remainder + self._cell_size
        else:
            return

        if is_vertical:
            self._pos_x = snapped
        else:
            self._pos_y = snapped

        self._direction = self._pending_direction

    def _check_for_wall(self, next_x, next_y, direction) -> bool:
        if self._direction in (Direction.UP, Direction.LEFT):
            cell_x = int(np.ceil(next_x / self._cell_size))
            cell_y = int(np.ceil(next_y / self._cell_size))
        else:
            cell_x = int(next_x // self._cell_size)
            cell_y = int(next_y // self._cell_size)

        if (
            cell_x < 0
            or cell_x >= self._maze.width
            or cell_y < 0
            or cell_y >= self._maze.height
        ):
            return True

        cell_idx = cell_y * self._maze.width + cell_x

        return self._maze.is_wall_direction(cell_idx, direction)

    def _get_cell_idx(self, x: int, y: int) -> int:
        if self._direction in (Direction.UP, Direction.LEFT):
            cell_x = int(np.ceil(x / self._cell_size))
            cell_y = int(np.ceil(y / self._cell_size))
        else:
            cell_x = int(x // self._cell_size)
            cell_y = int(y // self._cell_size)

        cell_x = max(0, min(cell_x, self._maze.width - 1))
        cell_y = max(0, min(cell_y, self._maze.height - 1))

        return cell_y * self._maze.width + cell_x

    def _get_next_step_xy(self, delta_time: float):
        if self._direction == Direction.UP:
            return self._pos_x, self._pos_y - (self._speed * delta_time)
        elif self._direction == Direction.DOWN:
            return self._pos_x, self._pos_y + (self._speed * delta_time)
        elif self._direction == Direction.LEFT:
            return self._pos_x - (self._speed * delta_time), self._pos_y
        elif self._direction == Direction.RIGHT:
            return self._pos_x + (self._speed * delta_time), self._pos_y

    def _load_assets(self, pac_size: int,
                     folder_path: str) -> List[NDArray[np.uint8]]:
        gen = walk(folder_path)
        files = [file for *_, file in gen]
        imgs: List[NDArray[np.uint8]] = []
        for file in files[0]:
            img = self._fb.get_image_array(f"{folder_path}/{file}",
                                           pac_size, pac_size)
            imgs.append(img)
        return imgs

    def _get_current_cell(self) -> Tuple[int, int]:

        cell_x = int(round(self._pos_x / self._cell_size))
        cell_y = int(round(self._pos_y / self._cell_size))

        cell_x = max(0, min(cell_x, self._maze.width - 1))
        cell_y = max(0, min(cell_y, self._maze.height - 1))

        return cell_x, cell_y

    def _snap_to_cell(self) -> None:

        self._pos_x = float(
            round(self._pos_x / self._cell_size) * self._cell_size
        )
        self._pos_y = float(
            round(self._pos_y / self._cell_size) * self._cell_size
        )

    def _is_close_to_cell_center(self) -> bool:

        tolerance = max(2.0, self._speed / 60.0)

        x_remainder = self._pos_x % self._cell_size
        y_remainder = self._pos_y % self._cell_size

        return (
            x_remainder <= tolerance
            or self._cell_size - x_remainder <= tolerance
        ) and (
            y_remainder <= tolerance
            or self._cell_size - y_remainder <= tolerance
        )
