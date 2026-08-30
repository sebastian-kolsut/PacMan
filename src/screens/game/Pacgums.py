from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext, Config
from .Maze import Maze

import numpy as np
from numpy.typing import NDArray
from typing import Tuple
import random

_KINDA_YELLOW = (71, 167, 222, 255)
_PINK = (231, 27, 250, 255)
_NICE = (3, 202, 253, 50)
# 198, 160, 250, 255


class Pacgums:
    """Owns the pacgum/super-pacgum layout, scoring and rendering."""

    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze, config: Config
                 ) -> None:
        """Place pacgums across the maze and super pacgums in its corners.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the pacgum sprites.
            maze: Maze to scatter pacgums across.
            config: Game configuration, used for the pacgum count and the
                points awarded for each kind of pacgum.
        """
        self._cell_size = cell_size
        self._size_pacgum = int(cell_size * 0.20)
        self._size_super = int(cell_size * 0.3)
        self._fb = FrameBuffer(mlx_ctx, self._size_pacgum, self._size_pacgum)
        self._img_pacgum = self._create_pacgum_image(self._size_pacgum,
                                                     mlx_ctx)
        self._img_super = self._create_pacgum_image(self._size_super, mlx_ctx)
        self._offset = cell_size // 2 - self._size_pacgum // 2
        self._super_offset = cell_size // 2 - self._size_super // 2
        self._maze = maze
        self._config = config
        pacgum_amount = config.levels[maze.level].pacgum
        self._layout = self._create_pacgum_layout(maze, pacgum_amount)
        self._super_layout = self._create_super_pacgum_layout(maze)
        self._points_per_pacgum = config.points_per_pacgum
        self._points_per_super = config.points_per_super_pacgum

    def is_level_won(self) -> bool:
        """Return whether every pacgum and super pacgum has been eaten."""
        return self._layout == 0 and self._super_layout == 0

    def clear_all(self) -> None:
        """Remove every remaining pacgum and super pacgum (level-skip)."""
        self._layout = 0
        self._super_layout = 0

    def draw_pacgums_to_image(self, image: NDArray[np.uint8],
                              maze_pos_x: int, maze_pos_y: int = 0) -> None:
        """Draw every remaining regular pacgum onto image.

        Args:
            image: Destination pixel buffer to draw onto.
            maze_pos_x: X offset of the maze's top-left corner on image.
            maze_pos_y: Y offset of the maze's top-left corner on image.
        """
        for i in range(self._maze.width * self._maze.height):
            if (self._layout & (1 << i)) != 0:
                x0 = (i % self._maze.width)
                y0 = i // self._maze.width
                x0, y0 = self._get_pacgum_position(x0, y0, self._offset)
                FrameBuffer.draw_clipped(
                    image, self._img_pacgum,
                    x0 + maze_pos_x, y0 + maze_pos_y)

    def draw_super_to_image(self, image: NDArray[np.uint8],
                            maze_pos_x: int, maze_pos_y: int = 0) -> None:
        """Draw every remaining super pacgum onto image.

        Args:
            image: Destination pixel buffer to draw onto.
            maze_pos_x: X offset of the maze's top-left corner on image.
            maze_pos_y: Y offset of the maze's top-left corner on image.
        """
        positions = [0, self._maze.width - 1,
                     (self._maze.width * self._maze.height) - 1,
                     self._maze.width * (self._maze.height - 1)]

        for i in positions:
            if (self._super_layout & (1 << i)) != 0:
                x0 = (i % self._maze.width)
                y0 = i // self._maze.width
                x0, y0 = self._get_pacgum_position(x0, y0, self._super_offset)
                FrameBuffer.draw_clipped(
                    image, self._img_super,
                    x0 + maze_pos_x, y0 + maze_pos_y)

    def _eat_pacgum_if_there(self, idx: int) -> tuple[int, bool]:
        """Remove and score whatever pacgum sits on cell idx, if any.

        Args:
            idx: Maze cell index to check and clear.

        Returns:
            A (points, ate_super) pair: the points earned (0 if nothing
            was there) and whether the eaten pacgum was a super pacgum.
        """
        if (self._layout & (1 << idx)) != 0:
            self._layout &= ~(1 << idx)
            return self._points_per_pacgum, False

        if (self._super_layout & (1 << idx)) != 0:
            self._super_layout &= ~(1 << idx)
            return self._points_per_super, True

        return 0, False

    def _get_pacgum_position(self, x: int, y: int, offset: int
                             ) -> Tuple[int, int]:
        """Return the top-left pixel position of a pacgum sprite in a cell.

        Args:
            x: Cell column.
            y: Cell row.
            offset: Pixel offset to center the sprite within the cell.

        Returns:
            The (x, y) pixel position to draw the sprite at.
        """
        return x * self._cell_size + offset, \
            y * self._cell_size + offset

    def _create_pacgum_layout(self, maze: Maze, pacgum_amount: int) -> int:
        """Randomly scatter pacgums across the maze's open cells.

        Args:
            maze: Maze to scatter pacgums across.
            pacgum_amount: Number of pacgums to place (clamped to the
                number of available cells).

        Returns:
            A bitboard with one bit set per cell that holds a pacgum.
        """
        layout = 0

        available_cells = [i for i in range(1, maze.width * maze.height)
                           if i not in maze.patters_positions and
                           i != maze.width - 1 and
                           i != (maze.width * maze.height) - 1 and
                           i != maze.width * (maze.height - 1)]

        pacgum_amount = min(pacgum_amount, len(available_cells))

        for _ in range(pacgum_amount):
            idx = random.choice(available_cells)
            layout |= (1 << idx)
            available_cells.remove(idx)

        return layout

    def _create_super_pacgum_layout(self, maze: Maze) -> int:
        """Place a super pacgum in each of the maze's four corners.

        Args:
            maze: Maze to place the super pacgums in.

        Returns:
            A bitboard with one bit set per corner cell.
        """
        layout = 0

        layout |= 1
        layout |= (1 << maze.width - 1)
        layout |= (1 << (maze.width * maze.height) - 1)
        layout |= (1 << maze.width * (maze.height - 1))

        return layout

    def _create_pacgum_image(self, size: int, mlx: MlxContext
                             ) -> NDArray[np.uint8]:
        """Render a filled circle sprite used for both pacgum kinds.

        Args:
            size: Width and height of the sprite in pixels.
            mlx: Window/rendering context used for the sprite buffer.

        Returns:
            The rendered circular pacgum sprite.
        """
        pacgum_img = FrameBuffer(mlx, size, size).get_array()
        pacgum_img[:, :] = [0, 0, 0, 255]
        center = size // 2

        h, w = pacgum_img.shape[:2]
        x, y = np.ogrid[:h, :w]

        distance_sq = (x - center)**2 + (y - center)**2
        mask = distance_sq < (size / 2)**2
        pacgum_img[mask] = _NICE

        return pacgum_img
