from src.models import Config, MlxContext
from src.models.dataclasses import ProgramState, Screen, GameState
from src.screens.game import (
    RenderMaze, Maze, PacMan, Pacgums, PauseScreen, LevelScreen,
)
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

_GHOST_EDIBLE_TIME = 7.0
_GHOST_BLINK_TIME = 2.0
_SEBA_LIKE_DURATION = 2.0
_OOPS_DURATION = 2.0

_SIDE_CHARACTER_ASPECT_RATIO = 725 / 1800
_SIDE_CHARACTER_HEIGHT_SCALE = 0.45
_SIDE_CHARACTER_GAP = 12

_NATA_COOL_ASSET = "assets/sebanata/NATA_COOL.png"
_NATA_BOO_ASSET = "assets/sebanata/NATA_BOO.png"
_NATA_OOPS_ASSET = "assets/sebanata/NATA_OOPS.png"
_SEBA_COOL_ASSET = "assets/sebanata/SEBA_COOL.png"
_SEBA_LIKE_ASSET = "assets/sebanata/SEBA_LIKE.png"
_SEBA_OOPS_ASSET = "assets/sebanata/SEBA_OOPS.png"


class PlayGame:
    def __init__(self, mlx_ctx: MlxContext, config: Config,
                 program_state: ProgramState) -> None:
        self._mlx_ctx = mlx_ctx
        self._program_state = program_state
        self._config = config
        self._maze = Maze(config)
        self._hud = HUD(config, mlx_ctx)
        self._lives = getattr(config, "lives", 3)
        self._game_over = False
        self._respawn_delay = 0.0
        self._ghost_edible_timer = 0.0
        self._pause = PauseScreen(mlx_ctx, program_state)
        self._level_screen = LevelScreen(mlx_ctx)
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._regenerate_maze_assets()
        self._seba_like_timer = 0.0
        self._oops_timer = 0.0
        self._last_pressed_key = 0

        self._keyboard = Display()
        self._direction_keycodes = {
            key: self._keyboard.keysym_to_keycode(key)
            for key in _DIRECTION_KEYS
        }

    def _regenerate_maze_assets(self) -> None:
        self._hud.reset_timer(
            self._config.levels[self._maze.level].level_max_time,
        )
        self._render_maze = RenderMaze(self._mlx_ctx, self._maze)
        self._hud.set_maze_bounds(
            self._render_maze.get_maze_position(),
            self._render_maze.fb.width,
        )
        cell_size = self._render_maze.get_cell_size()
        self._pacgums = Pacgums(
            cell_size, self._mlx_ctx, self._maze, self._config,
        )
        self._pac_man = PacMan(
            cell_size, self._mlx_ctx, self._maze, self._pacgums,
        )
        self._ghosts = [
            Blinky(cell_size, self._mlx_ctx, self._maze, (0, 0)),
            Clyde(
                cell_size,
                self._mlx_ctx,
                self._maze,
                (self._maze.width - 1, 0),
            ),
            Pinky(
                cell_size,
                self._mlx_ctx,
                self._maze,
                (self._maze.width - 1, self._maze.height - 1),
            ),
            Inky(
                cell_size,
                self._mlx_ctx,
                self._maze,
                (0, self._maze.height - 1),
            ),
        ]
        (
            self._side_character_width,
            self._side_character_height,
        ) = self._calculate_side_character_size()
        self._nata_cool = FrameBuffer.get_image_array(
            _NATA_COOL_ASSET,
            self._side_character_width,
            self._side_character_height,
        )
        self._nata_boo = FrameBuffer.get_image_array(
            _NATA_BOO_ASSET,
            self._side_character_width,
            self._side_character_height,
        )
        self._nata_oops = FrameBuffer.get_image_array(
            _NATA_OOPS_ASSET,
            self._side_character_width,
            self._side_character_height,
        )
        self._seba_cool = FrameBuffer.get_image_array(
            _SEBA_COOL_ASSET,
            self._side_character_width,
            self._side_character_height,
        )
        self._seba_like = FrameBuffer.get_image_array(
            _SEBA_LIKE_ASSET,
            self._side_character_width,
            self._side_character_height,
        )
        self._seba_oops = FrameBuffer.get_image_array(
            _SEBA_OOPS_ASSET,
            self._side_character_width,
            self._side_character_height,
        )
        self._replace_side_character_transparency_with_black()
        self._hud.set_level(self._maze.level + 1)
        self._level_screen.show(self._maze.level + 1)

    def _get_pressed_direction(self) -> int:
        keymap = self._keyboard.query_keymap()
        for key in _DIRECTION_KEYS:
            keycode = self._direction_keycodes[key]
            if keymap[keycode // 8] & (1 << (keycode % 8)):
                return key
        return 0

    def handle_key(self, keycode: int) -> str | None:
        return self._pause.update(keycode)

    def get_final_score(self) -> int:
        return self._hud.get_score()

    def update(self, delta_time: float) -> None:

        if self._game_over:
            self._program_state.screen = Screen.WIN_OR_LOSE
            self._program_state.state = GameState.LOST
            return

        if self._level_screen.is_active():
            self._level_screen.update(delta_time)
            return

        if self._pacgums.is_level_won():
            self._maze.level += 1
            if self._maze.level < len(self._config.levels):
                self._maze.generate_new_maze()
                self._regenerate_maze_assets()
            else:
                self._program_state.screen = Screen.WIN_OR_LOSE
                self._program_state.state = GameState.WON
            return

        if self._pause.is_game_paused():
            return
        if self._respawn_delay > 0:
            self._respawn_delay -= delta_time

        self._seba_like_timer = max(
            0.0,
            self._seba_like_timer - delta_time,
        )
        self._oops_timer = max(0.0, self._oops_timer - delta_time)

        self._update_ghost_edible_mode(delta_time)
        self._pac_man.update(delta_time, self._get_pressed_direction())

        if self._pac_man.ate_super_pacgum():
            self._activate_ghost_edible_mode()

        pacman_cell = self._pac_man.get_cell_position()
        pacman_direction = self._pac_man.get_direction()

        for ghost in self._ghosts:
            ghost.update(
                delta_time,
                pacman_cell,
                pacman_direction,
            )

        if self._respawn_delay <= 0:
            collided_ghost = self._get_collided_ghost()

            if collided_ghost is not None:
                if collided_ghost.is_frightened():
                    collided_ghost.eat()
                    self._pac_man.add_points(self._config.points_per_ghost)
                    self._seba_like_timer = _SEBA_LIKE_DURATION
                else:
                    self._lose_life()

                    if self._game_over:
                        self._program_state.screen = Screen.WIN_OR_LOSE
                        self._program_state.state = GameState.LOST
                        return

        if not self._hud.update(
            delta_time,
            self._pac_man.get_new_points(),
            self._lives,
        ):
            self._game_over = True
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
        self._draw_side_characters(pixels, maze_x, maze_img.shape[1])
        self._pacgums.draw_pacgums_to_image(pixels, maze_x)
        self._pacgums.draw_super_to_image(pixels, maze_x)
        self._fb.draw_blended_tile(
            pixels, pac_img,
            int(self._pac_man._pos_x) + self._pac_man._offset + maze_x,
            int(self._pac_man._pos_y) + self._pac_man._offset,
            )

        for ghost in self._ghosts:
            ghost_img = ghost.render()
            ghost_y, ghost_x = ghost.get_draw_position()

            self._fb.draw_blended_tile(
                pixels,
                ghost_img,
                ghost_x + maze_x,
                ghost_y,
            )

        self._hud.render(pixels)

        if self._pause.is_game_paused():
            self._pause.render(pixels)

        self._level_screen.render(pixels)

        self._fb.commit()
        self._fb.put_image_to_window()

    def get_image(self) -> np.ndarray:
        return self._fb.get_array()

    def _draw_side_characters(
        self,
        pixels: np.ndarray,
        maze_x: int,
        maze_width: int,
    ) -> None:
        if self._oops_timer > 0:
            nata_image = self._nata_oops
            seba_image = self._seba_oops
        else:
            nata_image = self._nata_boo if any(
                ghost.is_frightened() for ghost in self._ghosts
            ) else self._nata_cool
            seba_image = self._seba_like if self._seba_like_timer > 0 \
                else self._seba_cool
        y0 = self._mlx_ctx.win_height - self._side_character_height
        y1 = y0 + self._side_character_height
        x0_nata = maze_x - _SIDE_CHARACTER_GAP - self._side_character_width
        x1_nata = x0_nata + self._side_character_width
        x0_seba = maze_x + maze_width + _SIDE_CHARACTER_GAP
        x1_seba = x0_seba + self._side_character_width

        pixels[y0:y1, x0_nata:x1_nata] = nata_image.astype(np.uint8)
        pixels[y0:y1, x0_seba:x1_seba] = seba_image.astype(np.uint8)

    def _replace_side_character_transparency_with_black(self) -> None:
        self._nata_cool = self._blacken_transparent_pixels(self._nata_cool)
        self._nata_boo = self._blacken_transparent_pixels(self._nata_boo)
        self._nata_oops = self._blacken_transparent_pixels(self._nata_oops)
        self._seba_cool = self._blacken_transparent_pixels(self._seba_cool)
        self._seba_like = self._blacken_transparent_pixels(self._seba_like)
        self._seba_oops = self._blacken_transparent_pixels(self._seba_oops)

    @staticmethod
    def _blacken_transparent_pixels(
        image: np.ndarray,
    ) -> np.ndarray:
        opaque_black_bgra = (0, 0, 0, 255)
        new_image = np.array(image)
        not_fully_opaque = new_image[:, :, 3] < 255

        new_image[not_fully_opaque] = [*opaque_black_bgra]

        return new_image

    def _calculate_side_character_size(self) -> tuple[int, int]:
        maze_width = self._render_maze.fb.width
        maze_x = self._render_maze.get_maze_position()
        right_space = self._mlx_ctx.win_width - maze_x - maze_width
        available_width = max(1, min(maze_x, right_space)
                              - _SIDE_CHARACTER_GAP)
        target_height = int(
            self._mlx_ctx.win_height * _SIDE_CHARACTER_HEIGHT_SCALE
        )
        max_height_from_width = int(
            available_width / _SIDE_CHARACTER_ASPECT_RATIO
        )
        height = max(1, min(
            target_height,
            max_height_from_width,
        ))
        width = max(1, int(height * _SIDE_CHARACTER_ASPECT_RATIO))

        return width, height

    def _get_collided_ghost(self):
        pacman_x, pacman_y = self._pac_man.get_center_position()
        pacman_radius = self._pac_man.get_collision_radius()

        for ghost in self._ghosts:
            if ghost.is_eaten():
                continue

            ghost_x, ghost_y = ghost.get_center_position()
            ghost_radius = ghost.get_collision_radius()

            distance = hypot(
                pacman_x - ghost_x,
                pacman_y - ghost_y,
            )

            if distance <= pacman_radius + ghost_radius:
                return ghost

        return None

    def _lose_life(self) -> None:
        self._lives -= 1
        self._oops_timer = _OOPS_DURATION

        if self._lives <= 0:
            self._game_over = True
            return

        self._reset_characters()
        self._respawn_delay = 1.0

    def _reset_characters(self) -> None:
        self._pac_man.reset_position()

        for ghost in self._ghosts:
            ghost.reset_position()

    def _activate_ghost_edible_mode(self) -> None:
        self._ghost_edible_timer = _GHOST_EDIBLE_TIME

        for ghost in self._ghosts:
            ghost.set_frightened(True)

    def _update_ghost_edible_mode(self, delta_time: float) -> None:
        if self._ghost_edible_timer <= 0:
            return

        self._ghost_edible_timer -= delta_time

        if self._ghost_edible_timer <= 0:
            self._ghost_edible_timer = 0.0

            for ghost in self._ghosts:
                ghost.set_frightened(False)

            return

        if self._ghost_edible_timer <= _GHOST_BLINK_TIME:
            for ghost in self._ghosts:
                ghost.set_blinking(True)
