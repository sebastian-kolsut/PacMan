from pathlib import Path
import time

import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext
from src.screens.draw_utils.FrameBuffer import FrameBuffer


_ASSETS_DIR = Path("assets/menu")

_TITLE_WIDTH = 1200
_TITLE_HEIGHT = 415

_BUTTON_WIDTH = 660
_BUTTON_HEIGHT = 120

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
        (
            self._title_width,
            self._title_height,
            self._button_width,
            self._button_height,
            self._selected_button_width,
            self._selected_button_height,
        ) = self._calculate_asset_sizes()

        self._title = FrameBuffer.get_image_array(
            str(_ASSETS_DIR / "title.png"),
            self._title_width,
            self._title_height,
        )

        self._buttons = {
            "start": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "start_button.png"),
                self._button_width,
                self._button_height,
            ),
            "instructions": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "instructions_button.png"),
                self._button_width,
                self._button_height,
            ),
            "highscores": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "highscores_button.png"),
                self._button_width,
                self._button_height,
            ),
            "settings": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "settings_button.png"),
                self._button_width,
                self._button_height,
            ),
            "exit": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "exit_button.png"),
                self._button_width,
                self._button_height,
            ),
        }

        self._selected_buttons = {
            "start": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "start_button.png"),
                self._selected_button_width,
                self._selected_button_height,
            ),
            "instructions": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "instructions_button.png"),
                self._selected_button_width,
                self._selected_button_height,
            ),
            "highscores": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "highscores_button.png"),
                self._selected_button_width,
                self._selected_button_height,
            ),
            "settings": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "settings_button.png"),
                self._selected_button_width,
                self._selected_button_height,
            ),
            "exit": FrameBuffer.get_image_array(
                str(_ASSETS_DIR / "exit_button.png"),
                self._selected_button_width,
                self._selected_button_height,
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
            self._title_height
            + 20
            + len(self._actions) * self._button_height
            + (len(self._actions) - 1) * _BUTTON_GAP
        )
        title_y = max(20, (self._mlx_ctx.win_height - menu_height) // 2)

        first_button_y = title_y + self._title_height + 20

        self._draw_centered(self._title, center_x, title_y)

        for index, action in enumerate(self._actions):
            base_y = first_button_y + index * (
                self._button_height + _BUTTON_GAP
            )
            image = self._get_button_image(action, index)

            y = base_y - (image.shape[0] - self._button_height) // 2
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

    def _calculate_asset_sizes(self) -> tuple[int, int, int, int, int, int]:
        window_width = self._mlx_ctx.win_width
        window_height = self._mlx_ctx.win_height

        title_width = int(window_width * 0.75)
        title_height = int(title_width * _TITLE_HEIGHT / _TITLE_WIDTH)

        button_width = int(window_width * 0.42)
        button_height = int(button_width * _BUTTON_HEIGHT / _BUTTON_WIDTH)

        selected_button_width = int(button_width * 1.03)
        selected_button_height = int(button_height * 1.04)

        max_menu_height = int(window_height * 0.90)
        menu_height = (
            title_height
            + 20
            + len(self._actions) * button_height
            + (len(self._actions) - 1) * _BUTTON_GAP
        )

        if menu_height > max_menu_height:
            scale = max_menu_height / menu_height

            title_width = int(title_width * scale)
            title_height = int(title_height * scale)
            button_width = int(button_width * scale)
            button_height = int(button_height * scale)
            selected_button_width = int(selected_button_width * scale)
            selected_button_height = int(selected_button_height * scale)

        return (
            title_width,
            title_height,
            button_width,
            button_height,
            selected_button_width,
            selected_button_height,
        )
