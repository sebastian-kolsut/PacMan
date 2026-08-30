from src.screens.draw_utils import FrameBuffer, RenderText
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


_FONT_FILE = "assets/fonts/ByteBounce.ttf"
_FONT_SCALE = 0.15

_TINT = (0, 0, 0, 200)

_DISPLAY_DURATION = 0.7


class LevelScreen:
    """Brief "LEVEL n" overlay shown when a new level starts."""

    def __init__(self, mlx_ctx: MlxContext) -> None:
        """Initialize the overlay's fonts and off-screen buffer.

        Args:
            mlx_ctx: Window/rendering context to size the overlay to.
        """
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._render_txt = RenderText(_FONT_FILE, mlx_ctx, _FONT_SCALE)
        self._text_img = self._render_txt.put_text_to_image("LEVEL 1")
        self._timer = 0.0

    def show(self, level: int) -> None:
        """Start displaying the overlay for the given level number.

        Args:
            level: 1-based level number to display.
        """
        self._text_img = self._render_txt.put_text_to_image(
            f"LEVEL {level}")
        self._timer = _DISPLAY_DURATION

    def update(self, delta_time: float) -> None:
        """Count down the display timer.

        Args:
            delta_time: Seconds elapsed since the last update.
        """
        self._timer = max(0.0, self._timer - delta_time)

    def is_active(self) -> bool:
        """Return whether the overlay should currently be shown."""
        return self._timer > 0

    def render(self, image: NDArray[np.uint8]) -> None:
        """Draw the overlay on top of image if it is currently active.

        Args:
            image: Destination pixel buffer to draw onto.
        """
        if not self.is_active():
            return

        pixels = self._fb.get_array()
        pixels[:, :] = np.array(_TINT, dtype=np.uint8)

        x = (self._mlx_ctx.win_width - self._text_img.shape[1]) // 2
        y = (self._mlx_ctx.win_height - self._text_img.shape[0]) // 2
        self._fb.draw_blended_tile(pixels, self._text_img, x, y)

        self._fb.draw_blended_tile(image, pixels, 0, 0)
