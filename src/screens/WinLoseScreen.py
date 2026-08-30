import time

import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext, ProgramState, GameState
from src.screens.draw_utils import FrameBuffer, RenderText
from src.Highscores import Highscores


KEY_ESCAPE = 65307
KEY_ENTER = 65293
KEY_SPACE = 32
KEY_UP = 65362
KEY_DOWN = 65364
KEY_W = 119
KEY_S = 115
KEY_BACKSPACE = 65288

_DIGIT_KEYS = range(48, 58)
_UPPER_LETTER_KEYS = range(65, 91)
_LOWER_LETTER_KEYS = range(97, 123)

_ASSETS_DIR = "assets/menu/win_lose_pause_menu"
_GAME_OVER_IMAGE = f"{_ASSETS_DIR}/gameover.png"
_YOU_WON_IMAGE = f"{_ASSETS_DIR}/you_won.png"
_RESTART_BUTTON = f"{_ASSETS_DIR}/restart_button.png"
_MAIN_MENU_BUTTON = f"{_ASSETS_DIR}/main_menu_button.png"
_HIGHSCORES_BUTTON = f"{_ASSETS_DIR}/highscores_button.png"
_SETTINGS_BUTTON = f"{_ASSETS_DIR}/settings_button.png"

_ENTER_NAME_LABEL = "assets/menu/win_lose_pause_menu/enter_your_name_label.png"
_YOUR_SCORE_LABEL = "assets/menu/win_lose_pause_menu/your_score_label.png"

_INFO_LABEL_WIDTH = 760
_INFO_LABEL_HEIGHT = 155
_INFO_TEXT_GAP = 30
_INFO_ROW_GAP = 18

_INFO_FONT_SIZE = 0.075

_HEADER_WIDTH = 2027
_HEADER_HEIGHT = 776
_BUTTON_WIDTH = 1188
_BUTTON_HEIGHT = 180
_HEADER_WIDTH_SCALE = 0.5
_BUTTON_WIDTH_SCALE = 0.34
_BUTTON_GAP = 16

_KINDA_BLACK = (10, 0, 8, 255)
_TRANSPARENT = (0, 0, 0, 0)

_FONT_SIZE = 0.165
_TYPING_FIELD_Y = 0.6

_MAX_NAME_LEN = 10


class WinLoseScreen:
    """Shown after a game ends: outcome header, then either name entry
    for an eligible highscore or the restart/main-menu/etc. buttons."""

    def __init__(self, mlx_ctx: MlxContext, state: ProgramState) -> None:
        """Load the win/lose headers, labels and button assets.

        Args:
            mlx_ctx: Window/rendering context to size the screen to.
            state: Shared program state, read for whether the run was
                won or lost.
        """
        self._mlx_ctx = mlx_ctx
        self._state = state
        self._input_name = False
        self._checked = False
        self._name = ""
        self._render_txt = RenderText("assets/fonts/ByteBounce.ttf",
                                      mlx_ctx, _FONT_SIZE)
        self._info_render_txt = RenderText(
            "assets/fonts/ByteBounce.ttf",
            mlx_ctx,
            _INFO_FONT_SIZE,
        )
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )
        self._enter_name_label = FrameBuffer.get_image_array(
            _ENTER_NAME_LABEL,
            _INFO_LABEL_WIDTH,
            _INFO_LABEL_HEIGHT,
        )

        self._your_score_label = FrameBuffer.get_image_array(
            _YOUR_SCORE_LABEL,
            _INFO_LABEL_WIDTH,
            _INFO_LABEL_HEIGHT,
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
        """Handle one key press: name entry, or menu navigation/selection.

        Args:
            keycode: X11 keysym of the pressed key.

        Returns:
            The selected action string ("restart", "main_menu",
            "highscores" or "settings") if Enter/Space was pressed
            outside of name entry, otherwise None.
        """
        if self._input_name:
            if keycode == KEY_ENTER and self._name:
                self._input_name = False
                self._checked = True
                self._scores.add_score(self._name, self._score)
                self._scores.write_scores()
                self._name = ""
            elif keycode == KEY_BACKSPACE:
                self._name = self._name[:-1]
            if len(self._name) < _MAX_NAME_LEN:
                if keycode in _DIGIT_KEYS or keycode in _UPPER_LETTER_KEYS:
                    self._name += chr(keycode)
                elif keycode in _LOWER_LETTER_KEYS:
                    self._name += chr(keycode).upper()
            return None

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
            self._checked = False
            return actions[self._selected_index]

        return None

    def update(self, is_eligible: bool, scores: Highscores,
               score: int) -> None:
        """Update the current run's score and start name entry if eligible.

        Args:
            is_eligible: Whether score qualifies for the top-10
                leaderboard.
            scores: Highscores leaderboard to add the score to.
            score: The player's final score for this run.
        """
        self._scores = scores
        self._score = score
        if is_eligible and not self._checked:
            self._input_name = True
            return

    def render(self, game_image: NDArray[np.uint8]) -> None:
        """Draw the dimmed game frame, outcome header and name/buttons.

        Args:
            game_image: Final gameplay frame to dim and draw behind the
                win/lose overlay.
        """
        pixels = self._fb.get_array()
        pixels[:, :, :] = game_image
        FrameBuffer.draw_blended_tile(pixels, self._overlay, 0, 0)

        header = self._headers.get(self._state.state,
                                   self._headers[GameState.LOST])
        FrameBuffer.draw_blended_tile(
            pixels,
            header,
            self._header_x,
            self._header_y,
        )
        if self._input_name:
            self._draw_player_info(pixels)
        else:
            self._draw_buttons(pixels, header.shape[0])

        self._fb.commit()
        self._fb.put_image_to_window()

    def _load_header(self, path: str) -> NDArray[np.uint8]:
        """Load and recolor a win/lose header image to be transparent.

        Args:
            path: Path to the header image asset.

        Returns:
            The header image with its black background made transparent.
        """
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

    def _draw_info_row(
        self,
        img: NDArray[np.uint8],
        label_img: NDArray[np.uint8],
        value: str,
        y: int,
    ) -> None:
        """Draw one labeled row (e.g. "Enter your name: ___") onto img.

        Args:
            img: Destination pixel buffer to draw onto.
            label_img: Pre-rendered label image for this row.
            value: Text value to render next to the label.
            y: Y coordinate of the row.
        """
        value_img = self._info_render_txt.put_text_to_image(value)

        label_x = int(self._mlx_ctx.win_width * 0.26)
        value_x = label_x + label_img.shape[1] + _INFO_TEXT_GAP

        label_y = y
        value_y = y + (label_img.shape[0] - value_img.shape[0]) // 2

        FrameBuffer.draw_blended_tile(
            img,
            label_img,
            label_x,
            label_y,
        )

        FrameBuffer.draw_blended_tile(
            img,
            value_img,
            value_x,
            value_y,
        )

    def _draw_player_info(self, img: NDArray[np.uint8]) -> None:
        """Draw the name-entry and score rows shown while entering a name.

        Args:
            img: Destination pixel buffer to draw onto.
        """
        start_y = int(self._mlx_ctx.win_height * 0.48)
        name_value = self._name if self._name else "_"

        self._draw_info_row(
            img,
            self._enter_name_label,
            name_value,
            start_y,
        )

        score_y = start_y + _INFO_LABEL_HEIGHT + _INFO_ROW_GAP

        self._draw_info_row(
            img,
            self._your_score_label,
            str(self._score),
            score_y,
        )

    def _draw_typing_field(self, img: NDArray[np.uint8]) -> None:
        """Draw a plain "ENTER NAME: <name>" line, unused by the current
        label-based layout but kept for simple debugging renders.

        Args:
            img: Destination pixel buffer to draw onto.
        """
        txt = "ENTER NAME: "

        center_x = self._mlx_ctx.win_width // 2
        y = int(self._mlx_ctx.win_height * _TYPING_FIELD_Y)
        x = center_x - (self._render_txt.get_text_width(txt + self._name) // 2)

        txt_img = self._render_txt.put_text_to_image(txt + self._name)
        self._fb.draw_blended_tile(img, txt_img, x, y)

    def _load_button(
        self,
        path: str,
        width: int | None = None,
        height: int | None = None,
    ) -> NDArray[np.uint8]:
        """Load a button sprite, defaulting to the standard button size.

        Args:
            path: Path to the button image asset.
            width: Target width, or None to use the standard button width.
            height: Target height, or None to use the standard button
                height.

        Returns:
            The loaded button sprite.
        """
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
        """Draw the column of action buttons below the outcome header.

        Args:
            pixels: Destination pixel buffer to draw onto.
            header_height: Height of the outcome header, to place the
                first button below it.
        """
        first_button_y = self._header_y + header_height + _BUTTON_GAP

        for index, action in enumerate(self._get_actions()):
            image = self._get_button_image(action, index)
            y = first_button_y + index * (
                self._button_height + _BUTTON_GAP
            ) - (image.shape[0] - self._button_height) // 2
            FrameBuffer.draw_blended_tile(
                pixels,
                image,
                self._get_centered_x(image.shape[1]),
                y,
            )

    def _get_actions(self) -> list[str]:
        """Return the button actions available for the current outcome.

        Returns:
            The action list for GameState.WON or GameState.LOST,
            defaulting to the lost-state actions.
        """
        return self._actions_by_state.get(
            self._state.state,
            self._actions_by_state[GameState.LOST],
        )

    def _get_button_image(self, action: str, index: int) -> NDArray[np.uint8]:
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

    def _get_centered_x(self, width: int) -> int:
        """Return the x coordinate that horizontally centers a given width.

        Args:
            width: Width in pixels of the element to center.

        Returns:
            The x coordinate to draw the element at.
        """
        return (self._mlx_ctx.win_width - width) // 2
