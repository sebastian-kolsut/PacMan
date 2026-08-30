from pathlib import Path
import time

import numpy as np
from numpy.typing import NDArray

from src.Highscores import Highscores
from src.models.dataclasses import MlxContext
from src.screens.draw_utils import FrameBuffer, RenderText


_ASSETS_DIR = Path("assets/menu")

_TITLE_WIDTH = 1200
_TITLE_HEIGHT = 415

_BUTTON_WIDTH = 1188
_BUTTON_HEIGHT = 180

_BUTTON_GAP = 8
_SIDE_CHARACTER_GAP_SCALE = 0.015
_SIDE_CHARACTER_HEIGHT_SCALE = 0.90
_CHARACTER_ASPECT_RATIO = 725 / 1800

_TOP_HIGHSCORES_WIDTH = 600
_TOP_HIGHSCORES_HEIGHT = 1200
_TOP_HIGHSCORES_FONT_SCALE = 0.028
_LEADERBOARD_TOP_PADDING = 0.12
_LEADERBOARD_BOTTOM_PADDING = 0.96
_MAX_MENU_HIGHSCORES = 10

_WHITE = (255, 255, 255)
_GOLD = (0, 220, 255)

KEY_SPACE = 32
KEY_ENTER = 65293
KEY_UP = 65362
KEY_DOWN = 65364
KEY_W = 119
KEY_S = 115


class MainMenu:
    """Render and control the main menu screen."""

    def __init__(self, mlx_ctx: MlxContext, scores: Highscores) -> None:
        """Load the menu assets and size them to the current window.

        Args:
            mlx_ctx: Window/rendering context to size the menu to.
            scores: Highscores leaderboard, shown in the menu panel.
        """
        self._mlx_ctx = mlx_ctx
        self._scores = scores
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
        self._side_character_width, self._side_character_height = \
            self._calculate_side_character_size()
        self._top_highscores_height = self._get_buttons_height()
        self._top_highscores_width = int(
            self._top_highscores_height
            * _TOP_HIGHSCORES_WIDTH / _TOP_HIGHSCORES_HEIGHT
        )
        self._highscores_text = RenderText(
            "assets/fonts/ByteBounce.ttf",
            mlx_ctx,
            _TOP_HIGHSCORES_FONT_SCALE,
        )
        self._leaderboard_entries: tuple[tuple[str, int], ...] | None = None

        self._title = FrameBuffer.get_image_array(
            str(_ASSETS_DIR / "title2.png"),
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
        self._nata = FrameBuffer.get_image_array(
            str(_ASSETS_DIR / "NATA.png"),
            self._side_character_width,
            self._side_character_height,
        )
        self._seba = FrameBuffer.get_image_array(
            str(_ASSETS_DIR / "SEBA.png"),
            self._side_character_width,
            self._side_character_height,
        )
        self._top_highscores = FrameBuffer.get_image_array(
            str(_ASSETS_DIR / "top_highscores1.png"),
            self._top_highscores_width,
            self._top_highscores_height,
        )
        self._leaderboard_image = self._top_highscores.copy()

    def get_image(self) -> NDArray[np.uint8]:
        """Return the last rendered menu frame.

        Used as the dimmed background for the settings screen.
        """
        return self._fb.get_array()

    def handle_key(self, keycode: int) -> str | None:
        """Handle one key press: menu navigation or selecting an action.

        Args:
            keycode: X11 keysym of the pressed key.

        Returns:
            The selected action string if Enter/Space was pressed,
            otherwise None.
        """
        if keycode in (KEY_UP, KEY_W):
            self.move_selection_up()
            return None
        if keycode in (KEY_DOWN, KEY_S):
            self.move_selection_down()
            return None
        if keycode in (KEY_ENTER, KEY_SPACE):
            return self.get_selected_action()
        return None

    def render(self) -> None:
        """Draw the title, leaderboard, mascots and menu buttons."""
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
        buttons_height = (
            len(self._actions) * self._button_height
            + (len(self._actions) - 1) * _BUTTON_GAP
        )

        self._draw_centered(self._title, center_x, title_y)
        self._draw_menu_content(first_button_y, buttons_height)

        button_center_x = self._get_menu_layout()["button_center_x"]
        for index, action in enumerate(self._actions):
            base_y = first_button_y + index * (
                self._button_height + _BUTTON_GAP
            )
            image = self._get_button_image(action, index)

            y = base_y - (image.shape[0] - self._button_height) // 2
            self._draw_centered(image, button_center_x, y)

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
        """Return the sprite to use for one button, pulsing it if selected.

        Args:
            action: Action name identifying which button sprite to use.
            index: Position of this button in the menu.

        Returns:
            The (possibly enlarged, pulsing) button image to draw.
        """
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
        """Draw image horizontally centered on center_x at height y.

        Args:
            image: Image to draw.
            center_x: X coordinate to center the image on.
            y: Y coordinate of the image's top edge.
        """
        x = center_x - image.shape[1] // 2
        FrameBuffer.draw_blended_tile(
            self._fb.get_array(),
            image,
            x,
            y,
        )

    def _draw_menu_content(
        self,
        first_button_y: int,
        buttons_height: int,
    ) -> None:
        """Draw the mascots and leaderboard panel flanking the buttons.

        Args:
            first_button_y: Y coordinate of the first menu button.
            buttons_height: Total height of the button column.
        """
        layout = self._get_menu_layout()
        character_y = first_button_y + (
            buttons_height - self._side_character_height
        ) // 2

        FrameBuffer.draw_blended_tile(
            self._fb.get_array(),
            self._nata,
            layout["nata_x"],
            character_y,
        )
        self._update_leaderboard_image()
        FrameBuffer.draw_blended_tile(
            self._fb.get_array(),
            self._leaderboard_image,
            layout["leaderboard_x"],
            first_button_y,
        )
        FrameBuffer.draw_blended_tile(
            self._fb.get_array(),
            self._seba,
            layout["seba_x"],
            character_y,
        )

    def _get_menu_layout(self) -> dict[str, int]:
        """Compute the x positions of the mascots, buttons and leaderboard.

        Returns:
            A mapping with "nata_x", "button_center_x", "leaderboard_x"
            and "seba_x" keys.
        """
        gap = max(12, int(
            self._mlx_ctx.win_width * _SIDE_CHARACTER_GAP_SCALE
        ))
        content_width = (
            self._side_character_width
            + self._button_width
            + self._top_highscores_width
            + self._side_character_width
            + 3 * gap
        )
        content_x = max(0, (self._mlx_ctx.win_width - content_width) // 2)
        nata_x = content_x
        button_left = nata_x + self._side_character_width + gap
        leaderboard_x = button_left + self._button_width + gap
        seba_x = leaderboard_x + self._top_highscores_width + gap

        return {
            "nata_x": nata_x,
            "button_center_x": button_left + self._button_width // 2,
            "leaderboard_x": leaderboard_x,
            "seba_x": seba_x,
        }

    def _update_leaderboard_image(self) -> None:
        """Redraw the leaderboard panel if the top scores have changed."""
        entries = tuple(
            (record.name, record.score)
            for record in self._scores.get_leaderboard().root[
                :_MAX_MENU_HIGHSCORES
            ]
        )
        if entries == self._leaderboard_entries:
            return

        self._leaderboard_entries = entries
        self._leaderboard_image = self._top_highscores.copy()
        top_y = int(
            self._top_highscores_height * _LEADERBOARD_TOP_PADDING
        )
        bottom_y = int(
            self._top_highscores_height * _LEADERBOARD_BOTTOM_PADDING
        )
        row_height = (bottom_y - top_y) // _MAX_MENU_HIGHSCORES

        for index, (name, score) in enumerate(entries, start=1):
            y = top_y + (index - 1) * row_height
            text_height = self._highscores_text.get_text_height()
            self._draw_leaderboard_text(
                f"{index}.",
                0.16,
                y,
                align_right=True,
                color=_GOLD if index == 1 else _WHITE,
            )
            row_color = _GOLD if index == 1 else _WHITE
            self._draw_leaderboard_text(name, 0.24, y, color=row_color)
            self._draw_leaderboard_text(
                str(score),
                0.90,
                y + text_height,
                align_right=True,
                color=row_color,
            )

    def _draw_leaderboard_text(
        self,
        text: str,
        x_scale: float,
        y: int,
        align_right: bool = False,
        color: tuple[int, int, int] = _WHITE,
    ) -> None:
        """Draw one line of leaderboard text onto the leaderboard panel.

        Args:
            text: Text to render.
            x_scale: X position as a fraction of the leaderboard width.
            y: Y coordinate to draw the text at.
            align_right: If True, x_scale marks the text's right edge
                instead of its left edge.
            color: RGB color to tint the text.
        """
        image = self._highscores_text.put_text_to_image(text)
        image[:, :, :3] = color
        x = int(self._top_highscores_width * x_scale)
        if align_right:
            x -= image.shape[1]
        FrameBuffer.draw_blended_tile(self._leaderboard_image, image, x, y)

    def _calculate_asset_sizes(self) -> tuple[int, int, int, int, int, int]:
        """Compute the title/button sizes that fit the current window.

        Returns:
            A (title_width, title_height, button_width, button_height,
            selected_button_width, selected_button_height) tuple, scaled
            down further if the full menu would not fit vertically.
        """
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

    def _calculate_side_character_size(self) -> tuple[int, int]:
        """Compute the mascot sprite size that fits beside the buttons.

        Returns:
            A (width, height) pair sized to the button column's height.
        """
        height = max(1, int(
            self._get_buttons_height() * _SIDE_CHARACTER_HEIGHT_SCALE
        ))
        width = max(1, int(height * _CHARACTER_ASPECT_RATIO))

        return width, height

    def _get_buttons_height(self) -> int:
        """Return the total height in pixels of the button column."""
        return (
            len(self._actions) * self._button_height
            + (len(self._actions) - 1) * _BUTTON_GAP
        )
