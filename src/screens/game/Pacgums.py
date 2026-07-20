from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext, Config
from .Maze import Maze

import numpy as np
from numpy.typing import NDArray
from typing import Tuple
import random

_KINDA_YELLOW = (71, 167, 222, 255)
_PINK = (231, 27, 250, 255)


class Pacgums:
    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze, config: Config
                 ) -> None:
        self._cell_size = cell_size
        self._size_pacgum = int(cell_size * 0.18)
        self._size_super = int(cell_size * 0.3)
        self._fb = FrameBuffer(mlx_ctx, self._size_pacgum, self._size_pacgum)
        self._img_pacgum = self._create_pacgum_image(self._size_pacgum,
                                                     mlx_ctx)
        self._img_super = self._create_pacgum_image(self._size_super, mlx_ctx)
        self._offset = cell_size // 2 - self._size_pacgum // 2
        self._super_offset = cell_size // 2 - self._size_super // 2
        self._maze = maze
        self._layout = self._create_pacgum_layout(maze, config.pacgum)
        self._super_layout = self._create_super_pacgum_layout(maze)
        self._points_per_pacgum = config.points_per_pacgum
        self._points_per_super = config.points_per_super_pacgum

    def draw_pacgums_to_image(self, image: NDArray[np.uint8],
                              maze_pos_x: int) -> None:
        for i in range(self._maze.width * self._maze.height):
            if (self._layout & (1 << i)) != 0:
                x0 = (i % self._maze.width)
                y0 = i // self._maze.width
                x0, y0 = self._get_pacgum_position(x0, y0, self._offset)
                x1, y1 = x0 + self._size_pacgum + maze_pos_x, y0 \
                    + self._size_pacgum
                image[y0:y1, x0 + maze_pos_x:x1] = self._img_pacgum

    def draw_super_to_image(self, image: NDArray[np.uint8],
                            maze_pos_x: int) -> None:
        positions = [0, self._maze.width - 1,
                     (self._maze.width * self._maze.height) - 1,
                     self._maze.width * (self._maze.height - 1)]

        for i in positions:
            if (self._super_layout & (1 << i)) != 0:
                x0 = (i % self._maze.width)
                y0 = i // self._maze.width
                x0, y0 = self._get_pacgum_position(x0, y0, self._super_offset)
                x1, y1 = x0 + self._size_super + maze_pos_x, y0 \
                    + self._size_super
                image[y0:y1, x0 + maze_pos_x:x1] = self._img_super

    def _eat_pacgum_if_there(self, idx: int) -> int:
        if (self._layout & (1 << idx)) != 0:
            self._layout &= ~(1 << idx)
            return self._points_per_pacgum
        if (self._super_layout & (1 << idx)) != 0:
            self._super_layout &= ~(1 << idx)
            return self._points_per_super
        return 0

    def _get_pacgum_position(self, x: int, y: int, offset: int
                             ) -> Tuple[int, int]:
        return x * self._cell_size + offset, \
            y * self._cell_size + offset

    def _create_pacgum_layout(self, maze: Maze, pacgum_amount: int) -> int:
        layout = 0

        available_cells = [i for i in range(1, maze.width * maze.height)
                           if i not in maze.patters_positions and
                           i != maze.width - 1 and i !=
                           (maze.width * maze.height)
                           - 1 and maze.width * (maze.height - 1)]

        for _ in range(pacgum_amount):
            idx = random.choice(available_cells)
            layout |= (1 << idx)
            available_cells.remove(idx)

        return layout

    def _create_super_pacgum_layout(self, maze: Maze) -> int:
        layout = 0

        layout |= 1
        layout |= (1 << maze.width - 1)
        layout |= (1 << (maze.width * maze.height) - 1)
        layout |= (1 << maze.width * (maze.height - 1))

        return layout

    def _create_pacgum_image(self, size: int, mlx: MlxContext
                             ) -> NDArray[np.uint8]:
        pacgum_img = FrameBuffer(mlx, size, size).get_array()
        pacgum_img[:, :] = [0, 0, 0, 255]
        center = size // 2

        h, w = pacgum_img.shape[:2]
        x, y = np.ogrid[:h, :w]

        distance_sq = (x - center)**2 + (y - center)**2
        mask = distance_sq < (size / 2)**2
        pacgum_img[mask] = _PINK

        return pacgum_img
