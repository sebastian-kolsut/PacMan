from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext
from .Maze import Maze

import numpy as np
from numpy.typing import NDArray
from typing import Tuple
import random

_KINDA_YELLOW = (71, 167, 222, 255)


class Pacgums:
    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze, pacgum_amount: int) -> None:
        self._cell_size = cell_size
        self._size = int(cell_size * 0.18)
        self._fb = FrameBuffer(mlx_ctx, self._size, self._size)
        self._img = self._create_pacgum_image()
        self._offset = cell_size // 2 - self._size // 2
        self._maze = maze
        self._layout = self._create_pacgum_layout(maze, pacgum_amount)

    def draw_pacgums_to_image(self, image: NDArray[np.uint8],
                              maze_pos_x: int) -> None:
        for i in range(self._maze.width * self._maze.height):
            if (self._layout & (1 << i)) != 0:
                x = (i % self._maze.width)
                y = i // self._maze.width
                x, y = self._get_pacgum_position(x, y)
                self._fb.draw_blended_tile(image, self._img, y, x + maze_pos_x)

    def _eat_pacgum_if_there(self, idx: int) -> None:
        if (self._layout & (1 << idx)) != 0:
            self._layout &= ~(1 << idx)

    def _get_pacgum_position(self, x: int, y: int) -> Tuple[int, int]:
        return x * self._cell_size + self._offset, \
            y * self._cell_size + self._offset

    def _create_pacgum_layout(self, maze: Maze, pacgum_amount: int) -> int:
        layout = 0

        available_cells = [i for i in range(maze.width * maze.height)
                           if i not in maze.patters_positions]

        for _ in range(pacgum_amount):
            idx = random.choice(available_cells)
            layout |= (1 << idx)
            available_cells.remove(idx)

        return layout

    def _create_pacgum_image(self) -> NDArray[np.uint8]:
        pacgum_img = self._fb.get_array()
        pacgum_img[:, :] = [0, 0, 0, 0]
        center = self._size // 2

        h, w = pacgum_img.shape[:2]
        x, y = np.ogrid[:h, :w]

        distance_sq = (x - center)**2 + (y - center)**2
        mask = distance_sq < (self._size / 2)**2
        pacgum_img[mask] = _KINDA_YELLOW

        return pacgum_img
