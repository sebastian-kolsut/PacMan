import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext, ProgramState
from src.screens.draw_utils import FrameBuffer, RenderText
from src.screens.game.HUD.HUD import FONT_FILEPATH, FONT_SIZE, \
    CHEAT_FONT_SIZE
from src.screens.game.wall_themes import WALL_THEMES


KEY_ESCAPE = 65307
KEY_LEFT = 65361
KEY_RIGHT = 65363

_PANEL_IMAGE = "assets/menu/settings_panel.png"
_PANEL_ASPECT_RATIO = 1536 / 1024
_PANEL_MAX_WIDTH_SCALE = 0.75
_PANEL_MAX_HEIGHT_SCALE = 0.9

_OVERLAY_TINT = (0, 0, 0, 230)

_SWATCH_SIZE = 40
_LABEL_GAP = 16
_HINT_TEXT = "ESC to close"
_HINT_MARGIN = 24


class SettingsScreen:

    def __init__(self, mlx_ctx: MlxContext,
                 program_state: ProgramState) -> None:
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

        hint_render_txt = RenderText(FONT_FILEPATH, mlx_ctx, CHEAT_FONT_SIZE)
        self._hint_img = hint_render_txt.put_text_to_image(_HINT_TEXT)

    def handle_key(self, keycode: int) -> str | None:
        if keycode == KEY_ESCAPE:
            return "close"
        if keycode == KEY_LEFT:
            self._cycle_wall_theme(-1)
            return None
        if keycode == KEY_RIGHT:
            self._cycle_wall_theme(1)
            return None
        return None

    def render(
        self,
        background_image: NDArray[np.uint8],
        dim_background: bool = True,
    ) -> None:
        self._sync_color_label()

        pixels = self._fb.get_array()
        pixels[:, :] = background_image
        if dim_background:
            FrameBuffer.draw_blended_tile(pixels, self._overlay, 0, 0)

        FrameBuffer.draw_blended_tile(
            pixels, self._panel, self._panel_x, self._panel_y,
        )
        self._draw_color_picker(pixels)
        self._draw_close_hint(pixels)

        self._fb.commit()
        self._fb.put_image_to_window()

    def _cycle_wall_theme(self, step: int) -> None:
        self._program_state.wall_theme_index = (
            self._program_state.wall_theme_index + step
        ) % len(WALL_THEMES)

    def _sync_color_label(self) -> None:
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

    def _draw_color_picker(self, pixels: NDArray[np.uint8]) -> None:
        content_height = max(
            self._arrow_left_img.shape[0],
            self._color_label_img.shape[0],
            self._swatch_img.shape[0],
            self._arrow_right_img.shape[0],
        )
        row_width = (
            self._arrow_left_img.shape[1] + _LABEL_GAP
            + self._color_label_img.shape[1] + _LABEL_GAP
            + self._swatch_img.shape[1] + _LABEL_GAP
            + self._arrow_right_img.shape[1]
        )

        # Sit slightly above the panel's vertical center, leaving room
        # below for future settings rows.
        row_y = self._panel_y + int(self._panel.shape[0] * 0.45) \
            - content_height // 2
        row_y = max(0, min(row_y, self._mlx_ctx.win_height - content_height))
        row_x = (self._mlx_ctx.win_width - row_width) // 2
        row_x = max(0, min(row_x, self._mlx_ctx.win_width - row_width))

        arrow_left_y = row_y + (
            content_height - self._arrow_left_img.shape[0]
        ) // 2
        label_x = row_x + self._arrow_left_img.shape[1] + _LABEL_GAP
        label_y = row_y + (
            content_height - self._color_label_img.shape[0]
        ) // 2
        swatch_x = label_x + self._color_label_img.shape[1] + _LABEL_GAP
        swatch_y = row_y + (content_height - int(
            self._swatch_img.shape[0] * 0.8)) // 2
        arrow_right_x = swatch_x + self._swatch_img.shape[1] + _LABEL_GAP
        arrow_right_y = row_y + (
            content_height - self._arrow_right_img.shape[0]
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
        FrameBuffer.draw_blended_tile(
            pixels, self._arrow_right_img, arrow_right_x, arrow_right_y,
        )

    def _draw_close_hint(self, pixels: NDArray[np.uint8]) -> None:
        hint_x = (self._mlx_ctx.win_width - self._hint_img.shape[1]) // 2
        hint_x = max(0, min(hint_x,
                            self._mlx_ctx.win_width - self._hint_img.shape[1]))
        hint_y = self._panel_y + self._panel.shape[0] \
            - self._hint_img.shape[0] - _HINT_MARGIN
        hint_y = max(0, min(
            hint_y, self._mlx_ctx.win_height - self._hint_img.shape[0],
        ))

        FrameBuffer.draw_blended_tile(pixels, self._hint_img, hint_x, hint_y)

    def _calculate_panel_size(self) -> tuple[int, int]:
        max_width = int(self._mlx_ctx.win_width * _PANEL_MAX_WIDTH_SCALE)
        max_height = int(self._mlx_ctx.win_height * _PANEL_MAX_HEIGHT_SCALE)
        width = min(max_width, int(max_height * _PANEL_ASPECT_RATIO))
        height = int(width / _PANEL_ASPECT_RATIO)

        return max(1, width), max(1, height)
