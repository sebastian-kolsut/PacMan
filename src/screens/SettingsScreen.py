import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext, ProgramState
from src.screens.draw_utils import FrameBuffer, RenderText
from src.screens.game.HUD.HUD import FONT_FILEPATH, FONT_SIZE, \
    CHEAT_FONT_SIZE
from src.screens.game.wall_themes import WALL_THEMES


KEY_ESCAPE = 65307
KEY_LEFT = 65361
KEY_UP = 65362
KEY_RIGHT = 65363
KEY_DOWN = 65364

_PANEL_IMAGE = "assets/menu/settings_panel.png"
_PANEL_ASPECT_RATIO = 1536 / 1024
_PANEL_MAX_WIDTH_SCALE = 0.75
_PANEL_MAX_HEIGHT_SCALE = 0.9

_OVERLAY_TINT = (0, 0, 0, 230)

_SWATCH_SIZE = 40
_LABEL_GAP = 16
_HINT_TEXT = "ESC to close"
_HINT_MARGIN = 24

_ROW_GAP = 30

_OPTION_WALL_COLOR = 0
_OPTION_VOLUME = 1
_OPTION_COUNT = 2

_VOLUME_STEPS = 10
_SEGMENT_WIDTH = 26
_SEGMENT_HEIGHT = 34
_SEGMENT_GAP = 4
_SEGMENT_FILLED_COLOR = (255, 255, 255, 255)
_SEGMENT_EMPTY_COLOR = (90, 90, 90, 255)


class SettingsScreen:
    """Wall color and music volume options, reachable from the menu or
    the in-game pause screen."""

    def __init__(self, mlx_ctx: MlxContext,
                 program_state: ProgramState) -> None:
        """Load the settings panel and size it to the current window.

        Args:
            mlx_ctx: Window/rendering context to size the panel to.
            program_state: Shared program state, read and written for
                the active wall theme and music volume.
        """
        self._mlx_ctx = mlx_ctx
        self._program_state = program_state
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._overlay = np.full(
            (mlx_ctx.win_height, mlx_ctx.win_width, 4),
            _OVERLAY_TINT,
            dtype=np.uint8,
        )

        panel_width, panel_height = self._calculate_panel_size()
        self._panel = FrameBuffer.get_image_array(
            _PANEL_IMAGE, panel_width, panel_height,
        )
        self._panel_x = (mlx_ctx.win_width - panel_width) // 2
        self._panel_y = (mlx_ctx.win_height - panel_height) // 2

        self._render_txt = RenderText(FONT_FILEPATH, mlx_ctx, FONT_SIZE)
        self._arrow_left_img = self._render_txt.put_text_to_image("<")
        self._arrow_right_img = self._render_txt.put_text_to_image(">")
        self._shown_theme_index = -1
        self._color_label_img: NDArray[np.uint8] = np.zeros(
            (0, 0, 4), dtype=np.uint8)
        self._swatch_img: NDArray[np.uint8] = np.zeros(
            (0, 0, 4), dtype=np.uint8)
        self._sync_color_label()

        self._selected_option = _OPTION_WALL_COLOR
        self._volume_label_img = self._render_txt.put_text_to_image("Volume")
        self._segment_filled_img = np.full(
            (_SEGMENT_HEIGHT, _SEGMENT_WIDTH, 4),
            _SEGMENT_FILLED_COLOR, dtype=np.uint8,
        )
        self._segment_empty_img = np.full(
            (_SEGMENT_HEIGHT, _SEGMENT_WIDTH, 4),
            _SEGMENT_EMPTY_COLOR, dtype=np.uint8,
        )

        hint_render_txt = RenderText(FONT_FILEPATH, mlx_ctx, CHEAT_FONT_SIZE)
        self._hint_img = hint_render_txt.put_text_to_image(_HINT_TEXT)

    def handle_key(self, keycode: int) -> str | None:
        """Handle one key press: row selection or adjusting an option.

        Args:
            keycode: X11 keysym of the pressed key.

        Returns:
            "close" if Escape was pressed, otherwise None.
        """
        if keycode == KEY_ESCAPE:
            return "close"
        if keycode == KEY_UP:
            self._selected_option = (
                self._selected_option - 1
            ) % _OPTION_COUNT
            return None
        if keycode == KEY_DOWN:
            self._selected_option = (
                self._selected_option + 1
            ) % _OPTION_COUNT
            return None
        if keycode == KEY_LEFT:
            self._adjust_selected_option(-1)
            return None
        if keycode == KEY_RIGHT:
            self._adjust_selected_option(1)
            return None
        return None

    def _adjust_selected_option(self, step: int) -> None:
        """Apply a left/right adjustment to whichever row is selected.

        Args:
            step: -1 or 1, the direction to adjust the selected option in.
        """
        if self._selected_option == _OPTION_WALL_COLOR:
            self._cycle_wall_theme(step)
        else:
            self._adjust_volume(step)

    def _adjust_volume(self, step: int) -> None:
        """Change the music volume by step, clamped to a valid range.

        Args:
            step: -1 or 1, the direction to adjust the volume in.
        """
        self._program_state.music_volume = max(
            0, min(_VOLUME_STEPS, self._program_state.music_volume + step),
        )

    def render(
        self,
        background_image: NDArray[np.uint8],
        dim_background: bool = True,
    ) -> None:
        """Draw the settings panel over background_image.

        Args:
            background_image: Frame to draw the panel on top of (the
                main menu or the paused game screen).
            dim_background: Whether to darken background_image first;
                False when the caller (e.g. the pause screen) has
                already dimmed it.
        """
        self._sync_color_label()

        pixels = self._fb.get_array()
        pixels[:, :] = background_image
        if dim_background:
            FrameBuffer.draw_blended_tile(pixels, self._overlay, 0, 0)

        FrameBuffer.draw_blended_tile(
            pixels, self._panel, self._panel_x, self._panel_y,
        )

        color_content_height = self._color_row_content_height()
        color_row_y = self._panel_y + int(self._panel.shape[0] * 0.45) \
            - color_content_height // 2
        volume_row_y = color_row_y + color_content_height + _ROW_GAP

        self._draw_color_picker(pixels, color_row_y)
        self._draw_volume_bar(pixels, volume_row_y)
        self._draw_close_hint(pixels)

        self._fb.commit()
        self._fb.put_image_to_window()

    def _cycle_wall_theme(self, step: int) -> None:
        """Move to the next/previous wall color theme.

        Args:
            step: -1 or 1, the direction to cycle the theme in.
        """
        self._program_state.wall_theme_index = (
            self._program_state.wall_theme_index + step
        ) % len(WALL_THEMES)

    def _sync_color_label(self) -> None:
        """Redraw the wall color label/swatch if the active theme changed."""
        if self._program_state.wall_theme_index == self._shown_theme_index:
            return

        self._shown_theme_index = self._program_state.wall_theme_index
        theme = WALL_THEMES[self._shown_theme_index]
        self._color_label_img = self._render_txt.put_text_to_image(
            f"Wall Color: {theme.name}",
        )
        self._swatch_img = np.full(
            (_SWATCH_SIZE, _SWATCH_SIZE, 4), theme.base_color, dtype=np.uint8,
        )

    def _color_row_content_height(self) -> int:
        """Return the pixel height of the tallest element in the color row."""
        return int(max(
            self._arrow_left_img.shape[0],
            self._color_label_img.shape[0],
            self._swatch_img.shape[0],
            self._arrow_right_img.shape[0],
        ))

    def _volume_row_content_height(self) -> int:
        """Return the pixel height of the tallest element in the volume row."""
        return int(max(
            self._arrow_left_img.shape[0],
            self._volume_label_img.shape[0],
            _SEGMENT_HEIGHT,
            self._arrow_right_img.shape[0],
        ))

    def _draw_color_picker(self, pixels: NDArray[np.uint8],
                           row_y: int) -> None:
        """Draw the wall color row: label, swatch, and arrows if selected.

        Args:
            pixels: Destination pixel buffer to draw onto.
            row_y: Y coordinate of the row.
        """
        show_arrows = self._selected_option == _OPTION_WALL_COLOR
        content_height = self._color_row_content_height()
        row_width = (
            self._arrow_left_img.shape[1] + _LABEL_GAP
            + self._color_label_img.shape[1] + _LABEL_GAP
            + self._swatch_img.shape[1] + _LABEL_GAP
            + self._arrow_right_img.shape[1]
        )

        row_y = max(0, min(row_y, self._mlx_ctx.win_height - content_height))
        row_x = (self._mlx_ctx.win_width - row_width) // 2
        row_x = max(0, min(row_x, self._mlx_ctx.win_width - row_width))

        label_x = row_x + self._arrow_left_img.shape[1] + _LABEL_GAP
        label_y = row_y + (
            content_height - self._color_label_img.shape[0]
        ) // 2
        swatch_x = label_x + self._color_label_img.shape[1] + _LABEL_GAP
        swatch_y = row_y + (content_height - int(
            self._swatch_img.shape[0] * 0.8)) // 2
        arrow_right_x = swatch_x + self._swatch_img.shape[1] + _LABEL_GAP

        if show_arrows:
            arrow_left_y = row_y + (
                content_height - self._arrow_left_img.shape[0]
            ) // 2
            FrameBuffer.draw_blended_tile(
                pixels, self._arrow_left_img, row_x, arrow_left_y,
            )

        FrameBuffer.draw_blended_tile(
            pixels, self._color_label_img, label_x, label_y,
        )
        FrameBuffer.draw_blended_tile(
            pixels, self._swatch_img, swatch_x, swatch_y,
        )

        if show_arrows:
            arrow_right_y = row_y + (
                content_height - self._arrow_right_img.shape[0]
            ) // 2
            FrameBuffer.draw_blended_tile(
                pixels, self._arrow_right_img, arrow_right_x, arrow_right_y,
            )

    def _draw_volume_bar(self, pixels: NDArray[np.uint8],
                         row_y: int) -> None:
        """Draw the volume row: label, segmented bar, and arrows if selected.

        Args:
            pixels: Destination pixel buffer to draw onto.
            row_y: Y coordinate of the row.
        """
        show_arrows = self._selected_option == _OPTION_VOLUME
        content_height = self._volume_row_content_height()
        bar_width = _VOLUME_STEPS * _SEGMENT_WIDTH \
            + (_VOLUME_STEPS - 1) * _SEGMENT_GAP
        row_width = (
            self._arrow_left_img.shape[1] + _LABEL_GAP
            + self._volume_label_img.shape[1] + _LABEL_GAP
            + bar_width + _LABEL_GAP
            + self._arrow_right_img.shape[1]
        )

        row_y = max(0, min(row_y, self._mlx_ctx.win_height - content_height))
        row_x = (self._mlx_ctx.win_width - row_width) // 2
        row_x = max(0, min(row_x, self._mlx_ctx.win_width - row_width))

        label_x = row_x + self._arrow_left_img.shape[1] + _LABEL_GAP
        label_y = row_y + (
            content_height - self._volume_label_img.shape[0]
        ) // 2
        bar_x = label_x + self._volume_label_img.shape[1] + _LABEL_GAP
        bar_y = row_y + int((content_height - _SEGMENT_HEIGHT) * 1.38) // 2
        arrow_right_x = bar_x + bar_width + _LABEL_GAP

        if show_arrows:
            arrow_left_y = row_y + (
                content_height - self._arrow_left_img.shape[0]
            ) // 2
            FrameBuffer.draw_blended_tile(
                pixels, self._arrow_left_img, row_x, arrow_left_y,
            )

        FrameBuffer.draw_blended_tile(
            pixels, self._volume_label_img, label_x, label_y,
        )

        volume = self._program_state.music_volume
        for i in range(_VOLUME_STEPS):
            segment = self._segment_filled_img if i < volume \
                else self._segment_empty_img
            segment_x = bar_x + i * (_SEGMENT_WIDTH + _SEGMENT_GAP)
            FrameBuffer.draw_blended_tile(pixels, segment, segment_x, bar_y)

        if show_arrows:
            arrow_right_y = row_y + (
                content_height - self._arrow_right_img.shape[0]
            ) // 2
            FrameBuffer.draw_blended_tile(
                pixels, self._arrow_right_img, arrow_right_x, arrow_right_y,
            )

    def _draw_close_hint(self, pixels: NDArray[np.uint8]) -> None:
        """Draw the "ESC to close" hint near the bottom of the panel.

        Args:
            pixels: Destination pixel buffer to draw onto.
        """
        hint_x = (self._mlx_ctx.win_width - self._hint_img.shape[1]) // 2
        hint_x = max(0, min(hint_x,
                            self._mlx_ctx.win_width - self._hint_img.shape[1]))
        hint_y = self._panel_y + self._panel.shape[0] - \
            self._hint_img.shape[0] * 5

        FrameBuffer.draw_blended_tile(pixels, self._hint_img, hint_x, hint_y)

    def _calculate_panel_size(self) -> tuple[int, int]:
        """Compute the settings panel size that fits the current window.

        Returns:
            A (width, height) pair, capped to the window's max scale and
            matched to the panel image's aspect ratio.
        """
        max_width = int(self._mlx_ctx.win_width * _PANEL_MAX_WIDTH_SCALE)
        max_height = int(self._mlx_ctx.win_height * _PANEL_MAX_HEIGHT_SCALE)
        width = min(max_width, int(max_height * _PANEL_ASPECT_RATIO))
        height = int(width / _PANEL_ASPECT_RATIO)

        return max(1, width), max(1, height)
