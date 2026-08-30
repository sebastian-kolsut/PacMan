from .Maze import Maze
from .Character import Character
from .Pacgums import Pacgums
from src.models.dataclasses import MlxContext
from src.models import Direction

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
    """The player-controlled character: movement, animation and score."""

    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze, pacgums: Pacgums) -> None:
        """Spawn Pac-Man in the middle of the maze and load his animations.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the sprite buffer.
            maze: Maze Pac-Man moves through.
            pacgums: Pacgum layout, eaten as Pac-Man moves over cells.
        """
        super().__init__(cell_size, mlx_ctx, maze)
        self._pacgums = pacgums
        self._animation = 0
        self._points = 0
        self._ate_super_pacgum = False
        self._pos_x = \
            float((maze.width // 2 - 1) * cell_size) if maze.width % 2 == 0 \
            else float((maze.width // 2) * cell_size)
        self._pos_y = \
            float((maze.height // 2 - 1) * cell_size) if maze.height % 2 == 0 \
            else float((maze.height // 2) * cell_size)
        self._direction = Direction.RIGHT
        self._pending_direction = Direction.RIGHT
        self._save_start_state()

        self._assets = {
            Direction.UP: self._load_assets(self._character_size, _UP_FOLDER),
            Direction.RIGHT: self._load_assets(self._character_size,
                                               _RIGHT_FOLDER),
            Direction.DOWN: self._load_assets(self._character_size,
                                              _DOWN_FOLDER),
            Direction.LEFT: self._load_assets(self._character_size,
                                              _LEFT_FOLDER)
        }

    def update(self, delta_time: float, keycode: int) -> None:
        """Move Pac-Man for one frame and advance his chomp animation.

        Args:
            delta_time: Seconds elapsed since the last update.
            keycode: X11 keysym of the currently pressed movement key, or
                0 if none is pressed.
        """
        self._move_pac_man(keycode, delta_time)
        self._animation += 1
        if self._animation == 15:
            self._animation = 0

    def render(self) -> NDArray[np.uint8]:
        """Render and return Pac-Man's current animation frame.

        Returns:
            The RGBA sprite image for the current direction and frame.
        """
        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]
        self._fb.draw_blended_tile(
            pixels,
            self._assets[self._direction][self._animation // 5], 0, 0)

        return pixels

    def get_new_points(self) -> int:
        """Return and clear the points earned since the last call.

        Returns:
            Points earned since the previous call to get_new_points.
        """
        points = self._points
        self._points = 0
        return points

    def add_points(self, points: int) -> None:
        """Add points to Pac-Man's pending score.

        Args:
            points: Points to add (e.g. for eating a frightened ghost).
        """
        self._points += points

    def set_speed_multiplier(self, speed_multiplier: float) -> None:
        """Set Pac-Man's movement speed as a multiple of the cell size.

        Args:
            speed_multiplier: New speed, in cells per second.
        """
        self._speed = self._cell_size * speed_multiplier

    def get_cell_position(self) -> tuple[int, int]:
        """Return the maze cell Pac-Man currently occupies."""
        return self._get_current_cell()

    def get_direction(self) -> Direction:
        """Return Pac-Man's current facing/movement direction."""
        return self._direction

    def _move_pac_man(self, keycode: int, delta_time: float) -> None:
        """Apply input, move Pac-Man and eat any pacgum on his new cell.

        Args:
            keycode: X11 keysym of the currently pressed movement key, or
                0 if none is pressed.
            delta_time: Seconds elapsed since the last update.
        """
        if keycode in _DIRETCIONS:
            self._pending_direction = _DIRETCIONS[keycode]
        self._try_turn(delta_time)

        next_pac_x, next_pac_y = self._get_next_step_xy(delta_time)

        cell_idx = self._get_cell_idx(next_pac_x, next_pac_y)
        points, ate_super = self._pacgums._eat_pacgum_if_there(cell_idx)
        self._points += points

        if ate_super:
            self._ate_super_pacgum = True

        if self._check_for_wall(next_pac_x, next_pac_y, self._direction):
            self._snap_to_cell()
            return

        self._pos_x, self._pos_y = next_pac_x, next_pac_y

    def ate_super_pacgum(self) -> bool:
        """Return and clear whether a super pacgum was eaten this frame.

        Returns:
            True if a super pacgum was eaten since the last call, False
            otherwise.
        """
        ate_super = self._ate_super_pacgum
        self._ate_super_pacgum = False
        return ate_super
