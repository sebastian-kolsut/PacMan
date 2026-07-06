from src.models.dataclasses import MlxContext
from src.screens.Maze import Maze
from typing import Tuple, Dict
from .FrameBuffer import FrameBuffer
from PIL import Image
from numpy.typing import NDArray
import numpy as np


_UP = 1
_RIGHT = 2
_DOWN = 4
_LEFT = 8

_MAZE_WIDTH_SCALE = 0.7
_SCREEN_MARGIN = (1 - _MAZE_WIDTH_SCALE) / 2


class DrawMaze:

    def __init__(self, mlx_ctx: MlxContext, maze: Maze):
        self._maze = maze
        self._mlx_ctx = mlx_ctx
        maze_width_px, maze_height_px, cell_size = \
            self._get_maze_size_pixels(mlx_ctx)
        self._cell_size = cell_size

        self.fb = FrameBuffer(mlx_ctx, maze_width_px, maze_height_px)

        self._walls = self._load_walls()

    def get_img_ptr(self) -> int:
        return self.fb.img_ptr

    def get_maze_position(self):
        """Return the x coordinate that centers the maze horizontally."""
        return max(0, (self._mlx_ctx.win_width - self.fb.width) // 2)

    def draw(self) -> None:
        pixels = self.fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]

        # self.fb.draw_blended_tile(pixels, self._walls[0b1100], 20, 20)

        for y in range(self._maze.height):
            for x in range(self._maze.width):
                self._draw_cell_to_img(x, y, pixels)

        self.fb.commit()

    def _draw_cell_to_img(self, x: int, y: int,
                          pixels: NDArray[np.uint8]) -> None:
        bit_idx = y * self._maze.width + x
        mask = 0

        if self._maze.is_wall_up(bit_idx):
            mask |= _UP
        if self._maze.is_wall_right(bit_idx):
            mask |= _RIGHT
        if self._maze.is_wall_down(bit_idx):
            mask |= _DOWN
        if self._maze.is_wall_left(bit_idx):
            mask |= _LEFT

        self.fb.draw_blended_tile(pixels, self._walls[mask],
                                  y * self._cell_size, x * self._cell_size)

    def _get_maze_size_pixels(
            self, mlx_ctx: MlxContext
            ) -> Tuple[int, int, int]:
        target_maze_width = int(mlx_ctx.win_width * _MAZE_WIDTH_SCALE)

        max_cell_size_width = target_maze_width // self._maze.width
        max_cell_size_height = self._mlx_ctx.win_height // self._maze.height

        cell_size = max(1, min(max_cell_size_width, max_cell_size_height))

        maze_width_px = cell_size * self._maze.width
        maze_height_px = cell_size * self._maze.height

        return maze_width_px, maze_height_px, cell_size

    def _get_image_array(self, file_name: str) -> NDArray[np.uint8]:
        img = Image.open(file_name)
        r, g, b, a = img.split()
        img_bgra = Image.merge("RGBA", (b, g, r, a))
        resized = img_bgra.resize(
            (self._cell_size, self._cell_size),
            Image.Resampling.NEAREST
            )

        arr = np.array(resized)
        mask = np.all(arr == [51, 26, 17, 255], axis=-1)

        arr[mask] = [255, 184, 219, 255]
        return arr

    def _load_walls(self) -> Dict[int, NDArray[np.uint8]]:
        walls = {
            0b0000: self._get_image_array("assets/maze_walls/all.png"),
            0b0001: self._get_image_array(
                "assets/maze_walls/down-left-right.png"),
            0b0010: self._get_image_array(
                "assets/maze_walls/up-down-left.png"),
            0b0011: self._get_image_array("assets/maze_walls/down-left.png"),
            0b0100: self._get_image_array(
                "assets/maze_walls/up-left-right.png"),
            0b0101: self._get_image_array("assets/maze_walls/left-right.png"),
            0b0110: self._get_image_array("assets/maze_walls/up-left.png"),
            0b0111: self._get_image_array("assets/maze_walls/left.png"),
            0b1000: self._get_image_array(
                "assets/maze_walls/up-down-right.png"),
            0b1001: self._get_image_array("assets/maze_walls/down-right.png"),
            0b1010: self._get_image_array("assets/maze_walls/up-down.png"),
            0b1011: self._get_image_array("assets/maze_walls/down.png"),
            0b1100: self._get_image_array("assets/maze_walls/up-right.png"),
            0b1101: self._get_image_array("assets/maze_walls/right.png"),
            0b1110: self._get_image_array("assets/maze_walls/up.png"),
            0b1111: self._get_image_array("assets/maze_walls/closed.png")
            }

        return walls
