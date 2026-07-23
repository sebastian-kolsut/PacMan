from src.models import Config, MlxContext
from src.models.dataclasses import ProgramState, Screen, GameState
from src.screens.game import RenderMaze, Maze, PacMan, Pacgums, PauseScreen
from src.screens.game.ghosts import Blinky, Clyde, Pinky, Inky
from src.screens.game.HUD import HUD
from src.screens.draw_utils import FrameBuffer
from math import hypot

from Xlib.display import Display  # type: ignore[import-untyped]
import numpy as np


_W, _A, _S, _D = 119, 97, 115, 100
_A_UP, _A_RIGHT, _A_DOWN, _A_LEFT = 65362, 65363, 65364, 65361
_DIRECTION_KEYS = (_W, _A, _S, _D,
                   _A_UP, _A_RIGHT, _A_DOWN, _A_LEFT)


class PlayGame:
    def __init__(self, mlx_ctx: MlxContext, config: Config,
                 program_state: ProgramState) -> None:
        self._mlx_ctx = mlx_ctx
        self._program_state = program_state
        self._current_level = 0
        self._config = config
        self._maze = Maze(config)
        self._render_maze = RenderMaze(mlx_ctx, self._maze)
        cell_size = self._render_maze.get_cell_size()
        self._pacgums = Pacgums(cell_size, mlx_ctx, self._maze, config)
        self._hud = HUD(config, mlx_ctx)
        self._lives = getattr(config, "lives", 3)
        self._game_over = False
        self._respawn_delay = 0.0
        self._pause = PauseScreen(mlx_ctx, program_state)
        self._pac_man = PacMan(cell_size, mlx_ctx, self._maze, self._pacgums)
        self._ghosts = [
            Blinky(cell_size, mlx_ctx, self._maze, (0, 0)),
            Clyde(
                cell_size,
                mlx_ctx,
                self._maze,
                (self._maze.width - 1, 0),
            ),
            Pinky(
                cell_size,
                mlx_ctx,
                self._maze,
                (self._maze.width - 1, self._maze.height - 1),
            ),
            Inky(
                cell_size,
                mlx_ctx,
                self._maze,
                (0, self._maze.height - 1),
            ),
        ]
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._last_pressed_key = 0

        self._keyboard = Display()
        self._direction_keycodes = {
            key: self._keyboard.keysym_to_keycode(key)
            for key in _DIRECTION_KEYS
        }

    def _get_pressed_direction(self) -> int:
        keymap = self._keyboard.query_keymap()
        for key in _DIRECTION_KEYS:
            keycode = self._direction_keycodes[key]
            if keymap[keycode // 8] & (1 << (keycode % 8)):
                return key
        return 0

    def handle_key(self, keycode: int) -> None:
        self._pause.update(keycode)

    def update(self, delta_time: float) -> None:
        if self._game_over:
            self._program_state.screen = Screen.WIN_OR_LOSE
            self._program_state.state = GameState.LOST
            return

        if self._pacgums.is_level_won():
            self._program_state.screen = Screen.WIN_OR_LOSE
            self._program_state.state = GameState.WON

        if self._pause.is_game_paused():
            return
        if self._respawn_delay > 0:
            self._respawn_delay -= delta_time

        self._pac_man.update(delta_time, self._get_pressed_direction())

        if not self._hud.update(delta_time, self._pac_man.get_new_points(),
                                self._lives):
            self._game_over = True
            self._program_state.screen = Screen.WIN_OR_LOSE
            self._program_state.state = GameState.LOST
            return

        pacman_cell = self._pac_man.get_cell_position()
        pacman_direction = self._pac_man.get_direction()

        for ghost in self._ghosts:
            ghost.update(
                delta_time,
                pacman_cell,
                pacman_direction,
            )

        if self._respawn_delay <= 0 and self._has_ghost_collision():
            self._lose_life()

            if self._game_over:
                self._program_state.screen = Screen.WIN_OR_LOSE
                self._program_state.state = GameState.LOST
                return

    def render(self) -> None:
        maze_img = self._render_maze.render()
        pac_img = self._pac_man.render()

        pixels = self._fb.get_array()
        pixels[:, :] = np.array([0, 0, 0, 255])

        maze_x = self._render_maze.get_maze_position()

        pixels[:maze_img.shape[0], maze_x:maze_x+maze_img.shape[1], :3] = \
            maze_img[:, :, :3]
        self._pacgums.draw_pacgums_to_image(pixels, maze_x)
        self._pacgums.draw_super_to_image(pixels, maze_x)
        self._fb.draw_blended_tile(
            pixels, pac_img,
            int(self._pac_man._pos_y) + self._pac_man._offset,
            int(self._pac_man._pos_x) + self._pac_man._offset + maze_x
            )
        self._hud.render(pixels)

        for ghost in self._ghosts:
            ghost_img = ghost.render()
            ghost_y, ghost_x = ghost.get_draw_position()

            self._fb.draw_blended_tile(
                pixels,
                ghost_img,
                ghost_y,
                ghost_x + maze_x,
            )

        self._hud.render(pixels)

        if self._pause.is_game_paused():
            self._pause.render(pixels)

        self._fb.commit()
        self._fb.put_image_to_window()

    def _has_ghost_collision(self) -> bool:
        pacman_x, pacman_y = self._pac_man.get_center_position()
        pacman_radius = self._pac_man.get_collision_radius()

        for ghost in self._ghosts:
            ghost_x, ghost_y = ghost.get_center_position()
            ghost_radius = ghost.get_collision_radius()

            distance = hypot(
                pacman_x - ghost_x,
                pacman_y - ghost_y,
            )

            if distance <= pacman_radius + ghost_radius:
                return True

        return False

    def _lose_life(self) -> None:
        self._lives -= 1

        if self._lives <= 0:
            self._game_over = True
            return

        self._reset_characters()
        self._respawn_delay = 1.0

    def _reset_characters(self) -> None:
        self._pac_man.reset_position()

        for ghost in self._ghosts:
            ghost.reset_position()
