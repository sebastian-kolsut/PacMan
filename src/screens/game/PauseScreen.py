import time

from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext
from src.models.dataclasses import ProgramState, Screen

from numpy.typing import NDArray
import numpy as np


KEY_ESCAPE = 65307
KEY_ENTER = 65293
KEY_SPACE = 32
KEY_UP = 65362
KEY_DOWN = 65364
KEY_W = 119
KEY_S = 115

PAUSE_IMG_FILE = "assets/menu/win_lose_pause_menu/pause_sign_transparent.png"
RESUME_BUTTON_FILE = "assets/menu/win_lose_pause_menu/resume_button.png"
MAIN_MENU_BUTTON_FILE = "assets/menu/win_lose_pause_menu/main_menu_button.png"
RESTART_BUTTON_FILE = "assets/menu/win_lose_pause_menu/restart_button.png"
SETTINGS_BUTTON_FILE = "assets/menu/win_lose_pause_menu/settings_button.png"
_PAUSE_IMG_WIDTH = 2040
_PAUSE_IMG_HEIGHT = 780
_BUTTON_WIDTH = 1188
_BUTTON_HEIGHT = 180
_BUTTON_WIDTH_SCALE = 0.34
_BUTTON_GAP = 16

KINDA_BLACK = (10, 0, 8, 255)
TRANSPARENT = (0, 0, 0, 0)
MAIN_TINT = (0, 0, 0, 230)


class PauseScreen:
    def __init__(self, mlx_ctx: MlxContext, game_state: ProgramState) -> None:
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._img = self._fb.get_array()
        self._img[:, :] = np.array(MAIN_TINT, dtype=np.uint8)
        pause_width = int(mlx_ctx.win_width * 0.5)
        pause_height = int(pause_width * _PAUSE_IMG_HEIGHT / _PAUSE_IMG_WIDTH)
        self._img_pos_x = self._get_postion_x_centered(pause_width)
        self._img_pos_y = int(mlx_ctx.win_height * 0.1)
        self._pause_tile = self._fb.get_image_array(
            PAUSE_IMG_FILE, pause_width, pause_height)
        self._pause_tile = self._fb.swap_colors_in_image_color_to_color(
            KINDA_BLACK, TRANSPARENT, self._pause_tile
        )
        self._button_width = int(mlx_ctx.win_width * _BUTTON_WIDTH_SCALE)
        self._button_height = int(
            self._button_width * _BUTTON_HEIGHT / _BUTTON_WIDTH
        )
        self._selected_button_width = int(self._button_width * 1.03)
        self._selected_button_height = int(self._button_height * 1.04)
        self._actions = ["resume", "restart", "settings", "main_menu"]
        self._selected_index = 0
        self._buttons = {
            "resume": self._fb.get_image_array(
                RESUME_BUTTON_FILE,
                self._button_width,
                self._button_height,
            ),
            "main_menu": self._fb.get_image_array(
                MAIN_MENU_BUTTON_FILE,
                self._button_width,
                self._button_height,
            ),
            "restart": self._fb.get_image_array(
                RESTART_BUTTON_FILE,
                self._button_width,
                self._button_height,
            ),
            "settings": self._fb.get_image_array(
                SETTINGS_BUTTON_FILE,
                self._button_width,
                self._button_height,
            ),
        }
        self._selected_buttons = {
            "resume": self._fb.get_image_array(
                RESUME_BUTTON_FILE,
                self._selected_button_width,
                self._selected_button_height,
            ),
            "main_menu": self._fb.get_image_array(
                MAIN_MENU_BUTTON_FILE,
                self._selected_button_width,
                self._selected_button_height,
            ),
            "restart": self._fb.get_image_array(
                RESTART_BUTTON_FILE,
                self._selected_button_width,
                self._selected_button_height,
            ),
            "settings": self._fb.get_image_array(
                SETTINGS_BUTTON_FILE,
                self._selected_button_width,
                self._selected_button_height,
            ),
        }
        self._game_state = game_state
        self._is_paused = False

    def is_game_paused(self) -> bool:
        return self._is_paused

    def update(self, keycode: int) -> str | None:
        if not self._is_paused:
            if keycode == KEY_ESCAPE:
                self._is_paused = True
            return None

        if keycode == KEY_ESCAPE:
            self._is_paused = False
            self._game_state.screen = Screen.MAIN_MENU
            return None

        if keycode in (KEY_UP, KEY_W):
            self._selected_index = (self._selected_index - 1) % len(
                self._actions
            )
            return None

        if keycode in (KEY_DOWN, KEY_S):
            self._selected_index = (self._selected_index + 1) % len(
                self._actions
            )
            return None

        if keycode in (KEY_ENTER, KEY_SPACE):
            return self._activate_selected_action()

        return None

    def render(self, image: NDArray[np.uint8]) -> None:
        self._img[:, :] = np.array(MAIN_TINT, dtype=np.uint8)
        self._fb.draw_blended_tile(self._img, self._pause_tile,
                                   self._img_pos_x, self._img_pos_y)
        self._draw_buttons()

        self._fb.draw_blended_tile(image, self._img, 0, 0)

    def _draw_buttons(self) -> None:
        first_button_y = self._img_pos_y + self._pause_tile.shape[0] + \
            _BUTTON_GAP

        for index, action in enumerate(self._actions):
            image = self._get_button_image(action, index)
            y = first_button_y + index * (
                self._button_height + _BUTTON_GAP
            ) - (image.shape[0] - self._button_height) // 2
            x = self._get_postion_x_centered(image.shape[1])
            FrameBuffer.draw_blended_tile(self._img, image, x, y)

    def _get_button_image(
        self,
        action: str,
        index: int,
    ) -> NDArray[np.uint8]:
        if index != self._selected_index:
            return self._buttons[action]

        pulse_on = int(time.time() * 3) % 2 == 0
        if pulse_on:
            return self._selected_buttons[action]
        return self._buttons[action]

    def _activate_selected_action(self) -> str | None:
        action = self._actions[self._selected_index]

        if action == "resume":
            self._is_paused = False
            return None

        if action in ("restart", "settings"):
            return action

        self._is_paused = False
        self._game_state.screen = Screen.MAIN_MENU
        return None

    def _get_postion_x_centered(self, text_width: int):
        return (self._mlx_ctx.win_width // 2) - (text_width // 2)
