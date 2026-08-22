import numpy as np
from numpy.typing import NDArray

from src.models.dataclasses import MlxContext
from src.screens.draw_utils import FrameBuffer


KEY_ESCAPE = 65307

_PANEL_IMAGE = "assets/menu/settings_panel.png"
_PANEL_ASPECT_RATIO = 1536 / 1024
_PANEL_MAX_WIDTH_SCALE = 0.75
_PANEL_MAX_HEIGHT_SCALE = 0.9

_OVERLAY_TINT = (0, 0, 0, 230)


class SettingsScreen:

    def __init__(self, mlx_ctx: MlxContext) -> None:
        self._mlx_ctx = mlx_ctx
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

    def handle_key(self, keycode: int) -> str | None:
        if keycode == KEY_ESCAPE:
            return "close"
        return None

    def render(
        self,
        background_image: NDArray[np.uint8],
        dim_background: bool = True,
    ) -> None:
        pixels = self._fb.get_array()
        pixels[:, :] = background_image
        if dim_background:
            FrameBuffer.draw_blended_tile(pixels, self._overlay, 0, 0)

        FrameBuffer.draw_blended_tile(
            pixels, self._panel, self._panel_x, self._panel_y,
        )

        self._fb.commit()
        self._fb.put_image_to_window()

    def _calculate_panel_size(self) -> tuple[int, int]:
        max_width = int(self._mlx_ctx.win_width * _PANEL_MAX_WIDTH_SCALE)
        max_height = int(self._mlx_ctx.win_height * _PANEL_MAX_HEIGHT_SCALE)
        width = min(max_width, int(max_height * _PANEL_ASPECT_RATIO))
        height = int(width / _PANEL_ASPECT_RATIO)

        return max(1, width), max(1, height)
