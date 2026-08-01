import time

import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext, ProgramState, GameState
from src.screens.draw_utils.FrameBuffer import FrameBuffer


KEY_ESCAPE = 65307
KEY_ENTER = 65293
KEY_SPACE = 32
KEY_UP = 65362
KEY_DOWN = 65364
KEY_W = 119
KEY_S = 115

_ASSETS_DIR = "assets/menu/win_lose_pause_menu"
_GAME_OVER_IMAGE = f"{_ASSETS_DIR}/gameover.png"
_YOU_WON_IMAGE = f"{_ASSETS_DIR}/you_won.png"
_RESTART_BUTTON = f"{_ASSETS_DIR}/restart_button.png"
_MAIN_MENU_BUTTON = f"{_ASSETS_DIR}/main_menu_button.png"
_HIGHSCORES_BUTTON = f"{_ASSETS_DIR}/highscores_button.png"
_SETTINGS_BUTTON = f"{_ASSETS_DIR}/settings_button.png"

_HEADER_WIDTH = 2027
_HEADER_HEIGHT = 776
_BUTTON_WIDTH = 1188
_BUTTON_HEIGHT = 180
_HEADER_WIDTH_SCALE = 0.5
_BUTTON_WIDTH_SCALE = 0.34
_BUTTON_GAP = 16

_KINDA_BLACK = (10, 0, 8, 255)
_TRANSPARENT = (0, 0, 0, 0)


class WinLoseScreen:
    def __init__(self, mlx_ctx: MlxContext, state: ProgramState) -> None:
        self._mlx_ctx = mlx_ctx
        self._state = state
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )
        self._overlay = np.full(
            (mlx_ctx.win_height, mlx_ctx.win_width, 4),
            (0, 0, 0, 230),
            dtype=np.uint8,
        )
        self._header_width = int(mlx_ctx.win_width * _HEADER_WIDTH_SCALE)
        self._header_height = int(
            self._header_width * _HEADER_HEIGHT / _HEADER_WIDTH
        )
        self._header_x = self._get_centered_x(self._header_width)
        self._header_y = int(mlx_ctx.win_height * 0.14)
        self._headers = {
            GameState.WON: self._load_header(_YOU_WON_IMAGE),
            GameState.LOST: self._load_header(_GAME_OVER_IMAGE),
        }

        self._button_width = int(mlx_ctx.win_width * _BUTTON_WIDTH_SCALE)
        self._button_height = int(
            self._button_width * _BUTTON_HEIGHT / _BUTTON_WIDTH
        )
        self._selected_button_width = int(self._button_width * 1.03)
        self._selected_button_height = int(self._button_height * 1.04)
        self._actions_by_state = {
            GameState.WON: ["restart", "main_menu", "highscores"],
            GameState.LOST: ["restart", "main_menu", "settings"],
        }
        self._selected_index = 0
        self._buttons = {
            "restart": self._load_button(_RESTART_BUTTON),
            "main_menu": self._load_button(_MAIN_MENU_BUTTON),
            "highscores": self._load_button(_HIGHSCORES_BUTTON),
            "settings": self._load_button(_SETTINGS_BUTTON),
        }
        self._selected_buttons = {
            "restart": self._load_button(
                _RESTART_BUTTON,
                self._selected_button_width,
                self._selected_button_height,
            ),
            "main_menu": self._load_button(
                _MAIN_MENU_BUTTON,
                self._selected_button_width,
                self._selected_button_height,
            ),
            "highscores": self._load_button(
                _HIGHSCORES_BUTTON,
                self._selected_button_width,
                self._selected_button_height,
            ),
            "settings": self._load_button(
                _SETTINGS_BUTTON,
                self._selected_button_width,
                self._selected_button_height,
            ),
        }

    def handle_key(self, keycode: int) -> str | None:
        actions = self._get_actions()

        if keycode == KEY_ESCAPE:
            return "main_menu"

        if keycode in (KEY_UP, KEY_W):
            self._selected_index = (self._selected_index - 1) % len(actions)
            return None

        if keycode in (KEY_DOWN, KEY_S):
            self._selected_index = (self._selected_index + 1) % len(actions)
            return None

        if keycode in (KEY_ENTER, KEY_SPACE):
            return actions[self._selected_index]

        return None

    def render(self, game_image: NDArray[np.uint8]) -> None:
        pixels = self._fb.get_array()
        pixels[:, :, :] = game_image
        FrameBuffer.draw_blended_tile(pixels, self._overlay, 0, 0)

        header = self._headers.get(self._state.state, self._headers[GameState.LOST])
        FrameBuffer.draw_blended_tile(
            pixels,
            header,
            self._header_y,
            self._header_x,
        )
        self._draw_buttons(pixels, header.shape[0])

        self._fb.commit()
        self._fb.put_image_to_window()

    def _load_header(self, path: str) -> NDArray[np.uint8]:
        image = FrameBuffer.get_image_array(
            path,
            self._header_width,
            self._header_height,
        )
        return FrameBuffer.swap_colors_in_image_color_to_color(
            _KINDA_BLACK,
            _TRANSPARENT,
            image,
        )

    def _load_button(
        self,
        path: str,
        width: int | None = None,
        height: int | None = None,
    ) -> NDArray[np.uint8]:
        return FrameBuffer.get_image_array(
            path,
            width or self._button_width,
            height or self._button_height,
        )

    def _draw_buttons(
        self,
        pixels: NDArray[np.uint8],
        header_height: int,
    ) -> None:
        first_button_y = self._header_y + header_height + _BUTTON_GAP

        for index, action in enumerate(self._get_actions()):
            image = self._get_button_image(action, index)
            y = first_button_y + index * (
                self._button_height + _BUTTON_GAP
            ) - (image.shape[0] - self._button_height) // 2
            FrameBuffer.draw_blended_tile(
                pixels,
                image,
                y,
                self._get_centered_x(image.shape[1]),
            )

    def _get_actions(self) -> list[str]:
        return self._actions_by_state.get(
            self._state.state,
            self._actions_by_state[GameState.LOST],
        )

    def _get_button_image(self, action: str, index: int) -> NDArray[np.uint8]:
        if index != self._selected_index:
            return self._buttons[action]

        pulse_on = int(time.time() * 3) % 2 == 0
        if pulse_on:
            return self._selected_buttons[action]
        return self._buttons[action]

    def _get_centered_x(self, width: int) -> int:
        return (self._mlx_ctx.win_width - width) // 2
