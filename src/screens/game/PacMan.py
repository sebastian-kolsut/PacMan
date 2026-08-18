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
    def __init__(self, cell_size: int, mlx_ctx: MlxContext,
                 maze: Maze, pacgums: Pacgums) -> None:
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

    def update(self, delta_time: float, keycode: int):
        self._move_pac_man(keycode, delta_time)
        self._animation += 1
        if self._animation == 15:
            self._animation = 0

    def render(self) -> NDArray[np.uint8]:
        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]
        self._fb.draw_blended_tile(
            pixels,
            self._assets[self._direction][self._animation // 5], 0, 0)

        return pixels

    def get_new_points(self) -> int:
        points = self._points
        self._points = 0
        return points

    def add_points(self, points: int) -> None:
        self._points += points

    def set_speed_multiplier(self, speed_multiplier: float) -> None:
        self._speed = self._cell_size * speed_multiplier

    def get_cell_position(self) -> tuple[int, int]:
        return self._get_current_cell()

    def get_direction(self) -> Direction:
        return self._direction

    def _move_pac_man(self, keycode: int, delta_time: float):
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
        ate_super = self._ate_super_pacgum
        self._ate_super_pacgum = False
        return ate_super
