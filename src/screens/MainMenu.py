from pathlib import Path
import time

import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext
from src.screens.draw_utils.FrameBuffer import FrameBuffer


_ASSETS_DIR = Path("assets/menu")

_TITLE_WIDTH = 760
_TITLE_HEIGHT = 215

_BUTTON_WIDTH = 480
_BUTTON_HEIGHT = 129

_SELECTED_BUTTON_WIDTH = 510
_SELECTED_BUTTON_HEIGHT = 137

_BUTTON_GAP = 8

KEY_SPACE = 32
KEY_ENTER = 65293
KEY_UP = 65362
KEY_DOWN = 65364


class MainMenu:
    """Render and control the main menu screen."""

    def __init__(self, mlx_ctx: MlxContext) -> None:
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )

        self._selected_index = 0
        self._actions = [
            "start",
            "instructions",
            "highscores",
            "settings",
            "exit",
        ]

        self._title = FrameBuffer.get_image_array(
            str(_ASSETS_DIR / "title.png"),
            _TITLE_WIDTH,
            _TITLE_HEIGHT,
        )

        self._buttons = {
            "start": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "start_button.png"),
                _BUTTON_WIDTH,
                _BUTTON_HEIGHT,
            ),
            "instructions": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "instructions_button.png"),
                _BUTTON_WIDTH,
                _BUTTON_HEIGHT,
            ),
            "highscores": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "highscores_button.png"),
                _BUTTON_WIDTH,
                _BUTTON_HEIGHT,
            ),
            "settings": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "settings_button.png"),
                _BUTTON_WIDTH,
                _BUTTON_HEIGHT,
            ),
            "exit": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "exit_button.png"),
                _BUTTON_WIDTH,
                _BUTTON_HEIGHT,
            ),
        }

        self._selected_buttons = {
            "start": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "start_button.png"),
                _SELECTED_BUTTON_WIDTH,
                _SELECTED_BUTTON_HEIGHT,
            ),
            "instructions": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "instructions_button.png"),
                _SELECTED_BUTTON_WIDTH,
                _SELECTED_BUTTON_HEIGHT,
            ),
            "highscores": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "highscores_button.png"),
                _SELECTED_BUTTON_WIDTH,
                _SELECTED_BUTTON_HEIGHT,
            ),
            "settings": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "settings_button.png"),
                _SELECTED_BUTTON_WIDTH,
                _SELECTED_BUTTON_HEIGHT,
            ),
            "exit": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "exit_button.png"),
                _SELECTED_BUTTON_WIDTH,
                _SELECTED_BUTTON_HEIGHT,
            ),
        }

    def handle_key(self, keycode: int) -> str | None:
        if keycode == KEY_UP:
            self.move_selection_up()
            return None
        if keycode == KEY_DOWN:
            self.move_selection_down()
            return None
        if keycode in (KEY_ENTER, KEY_SPACE):
            return self.get_selected_action()
        return None

    def render(self) -> None:
        pixels = self._fb.get_array()
        pixels[:, :, :] = np.array([0, 0, 0, 255], dtype=np.uint8)

        center_x = self._mlx_ctx.win_width // 2

        menu_height = (
            _TITLE_HEIGHT
            + 20
            + len(self._actions) * _BUTTON_HEIGHT
            + (len(self._actions) - 1) * _BUTTON_GAP
        )
        title_y = max(50, (self._mlx_ctx.win_height - menu_height) // 2)

        first_button_y = title_y + _TITLE_HEIGHT + 20

        self._draw_centered(self._title, center_x, title_y)

        for index, action in enumerate(self._actions):
            y = first_button_y + index * (_BUTTON_HEIGHT + _BUTTON_GAP)
            image = self._get_button_image(action, index)
            self._draw_centered(image, center_x, y)

        self._fb.commit()
        self._mlx_ctx.m.mlx_put_image_to_window(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            self._fb.img_ptr,
            0,
            0,
        )

    def move_selection_up(self) -> None:
        """Move selected menu button up."""
        self._selected_index = (
            self._selected_index - 1
        ) % len(self._actions)

    def move_selection_down(self) -> None:
        """Move selected menu button down."""
        self._selected_index = (
            self._selected_index + 1
        ) % len(self._actions)

    def get_selected_action(self) -> str:
        """Return the currently selected menu action."""
        return self._actions[self._selected_index]

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

    def _draw_centered(
        self,
        image: NDArray[np.uint8],
        center_x: int,
        y: int,
    ) -> None:
        x = center_x - image.shape[1] // 2
        FrameBuffer.draw_blended_tile(
            self._fb.get_array(),
            image,
            y,
            x,
        )
