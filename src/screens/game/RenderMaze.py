from src.models.dataclasses import MlxContext, ProgramState
from src.screens.game.Maze import Maze
from src.screens.game.wall_themes import WALL_THEMES
from typing import Tuple, Dict
from src.screens.draw_utils import FrameBuffer
from numpy.typing import NDArray
import numpy as np


_UP = 1
_RIGHT = 2
_DOWN = 4
_LEFT = 8

_MAZE_WIDTH_SCALE = 0.7

_PATTERN_CELL = 0b1111

_NO_COLOR = (0, 0, 0, 0)


class RenderMaze:
    """Renders the maze's walls (and the decorative "42" pattern) to an
    off-screen buffer, sized and centered to fit the game window."""

    def __init__(self, mlx_ctx: MlxContext, maze: Maze,
                 program_state: ProgramState):
        """Size the maze to the window and load its wall tile assets.

        Args:
            mlx_ctx: Window/rendering context to size the maze to.
            maze: Maze to render.
            program_state: Shared program state, read for the active wall
                color theme.
        """
        self._maze = maze
        self._mlx_ctx = mlx_ctx
        self._program_state = program_state

        self._theme_index = program_state.wall_theme_index
        theme = WALL_THEMES[self._theme_index]
        self._base_color = theme.base_color
        self._pattern_color = theme.pattern_color

        maze_width_px, maze_height_px, cell_size = \
            self._get_maze_size_pixels(self._mlx_ctx)
        self._cell_size = cell_size

        self.fb = FrameBuffer(self._mlx_ctx, maze_width_px, maze_height_px)

        self._walls = self._load_walls()
        self._pixels = self.fb.get_array()

    def get_img_ptr(self) -> int:
        """Return the MLX image pointer backing the rendered maze."""
        return int(self.fb.img_ptr)

    def get_maze_position(self) -> int:
        """Return the x coordinate that centers the maze horizontally."""
        return max(0, (self._mlx_ctx.win_width - self.fb.width) // 2)

    def get_maze_position_y(self) -> int:
        """Return the y coordinate that centers the maze vertically."""
        return max(0, (self._mlx_ctx.win_height - self.fb.height) // 2)

    def get_cell_size(self) -> int:
        """Return the size in pixels of one maze cell."""
        return self._cell_size

    def render(self) -> NDArray[np.uint8]:
        """Render the maze walls, redrawing only when the maze changed.

        Returns:
            The rendered maze image, reused across frames until the maze
            is regenerated or the wall theme changes.
        """
        self._sync_wall_theme()

        if self._maze.dirty:
            return self._pixels

        self._pixels = self.fb.get_array()
        self._pixels[:, :] = [0, 0, 0, 0]

        # self.fb.draw_blended_tile(pixels, self._walls[0b1100], 20, 20)

        for y in range(self._maze.height):
            for x in range(self._maze.width):
                self._draw_cell_to_img(x, y, self._pixels)

        self._maze.dirty = True

        return self._pixels

    def _draw_cell_to_img(self, x: int, y: int,
                          pixels: NDArray[np.uint8]) -> None:
        """Draw one maze cell's wall tile, swapping in the "42" pattern.

        Args:
            x: Cell column.
            y: Cell row.
            pixels: Destination pixel buffer to draw onto.
        """
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

        img = self._walls[mask]

        if mask == _PATTERN_CELL:
            mask = self._get_pattern_mask(bit_idx)
            img = self.fb.swap_colors_in_image_leave_out(
                self._base_color, self._pattern_color, self._walls[mask])

        self.fb.draw_blended_tile(pixels, img,
                                  x * self._cell_size, y * self._cell_size)

    def _get_pattern_mask(self, idx: int) -> int:
        """Return the wall tile mask that continues the "42" pattern.

        Args:
            idx: Cell index of a fully-enclosed (pattern) cell.

        Returns:
            A wall bitmask with the sides facing neighboring pattern
            cells cleared, so the pattern reads as connected tiles.
        """
        mask = _PATTERN_CELL

        up = idx - self._maze.width in self._maze.patters_positions
        right = idx + 1 in self._maze.patters_positions
        down = idx + self._maze.width in self._maze.patters_positions
        left = idx - 1 in self._maze.patters_positions

        if up:
            mask &= ~_UP
        if right:
            mask &= ~_RIGHT
        if down:
            mask &= ~_DOWN
        if left:
            mask &= ~_LEFT

        return mask

    def _get_maze_size_pixels(
            self, mlx_ctx: MlxContext
            ) -> Tuple[int, int, int]:
        """Compute the maze's pixel size and cell size to fit the window.

        Args:
            mlx_ctx: Window/rendering context to fit the maze into.

        Returns:
            A (maze_width_px, maze_height_px, cell_size) triple.
        """
        target_maze_width = int(mlx_ctx.win_width * _MAZE_WIDTH_SCALE)

        max_cell_size_width = target_maze_width // self._maze.width
        max_cell_size_height = self._mlx_ctx.win_height // self._maze.height

        cell_size = max(1, min(max_cell_size_width, max_cell_size_height))

        maze_width_px = cell_size * self._maze.width
        maze_height_px = cell_size * self._maze.height

        return maze_width_px, maze_height_px, cell_size

    def _sync_wall_theme(self) -> None:
        """Recolor the wall tiles if the active theme changed."""
        if self._program_state.wall_theme_index == self._theme_index:
            return

        theme = WALL_THEMES[self._program_state.wall_theme_index]
        for mask, tile in self._walls.items():
            self._walls[mask] = self.fb.swap_colors_in_image_color_to_color(
                self._base_color, theme.base_color, tile)

        self._theme_index = self._program_state.wall_theme_index
        self._base_color = theme.base_color
        self._pattern_color = theme.pattern_color
        self._maze.dirty = False

    def _get_image_array_wall(self, file_name: str) -> NDArray[np.uint8]:
        """Load one wall tile asset, recolored to the active theme.

        Args:
            file_name: Path to the wall tile image.

        Returns:
            The loaded tile, recolored from transparent to the theme's
            base wall color.
        """
        img = self.fb.get_image_array(file_name, self._cell_size,
                                      self._cell_size)
        img = self.fb.swap_colors_in_image_leave_out(
            _NO_COLOR, self._base_color, img)

        return img

    def _load_walls(self) -> Dict[int, NDArray[np.uint8]]:
        """Load every wall tile variant, keyed by its wall-side bitmask.

        Returns:
            A mapping from wall-side bitmask to the matching tile image.
        """
        walls = {
            0b0000: self._get_image_array_wall("assets/maze_walls/all.png"),
            0b0001: self._get_image_array_wall(
                "assets/maze_walls/down-left-right.png"),
            0b0010: self._get_image_array_wall(
                "assets/maze_walls/up-down-left.png"),
            0b0011: self._get_image_array_wall(
                "assets/maze_walls/down-left.png"),
            0b0100: self._get_image_array_wall(
                "assets/maze_walls/up-left-right.png"),
            0b0101: self._get_image_array_wall(
                "assets/maze_walls/left-right.png"),
            0b0110: self._get_image_array_wall(
                "assets/maze_walls/up-left.png"),
            0b0111: self._get_image_array_wall("assets/maze_walls/left.png"),
            0b1000: self._get_image_array_wall(
                "assets/maze_walls/up-down-right.png"),
            0b1001: self._get_image_array_wall(
                "assets/maze_walls/down-right.png"),
            0b1010: self._get_image_array_wall(
                "assets/maze_walls/up-down.png"),
            0b1011: self._get_image_array_wall("assets/maze_walls/down.png"),
            0b1100: self._get_image_array_wall(
                "assets/maze_walls/up-right.png"),
            0b1101: self._get_image_array_wall("assets/maze_walls/right.png"),
            0b1110: self._get_image_array_wall("assets/maze_walls/up.png"),
            0b1111: self._get_image_array_wall("assets/maze_walls/closed.png")
            }

        return walls
