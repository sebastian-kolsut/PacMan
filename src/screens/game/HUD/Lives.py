from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext

from typing import Tuple
from numpy.typing import NDArray
import numpy as np


_SPRITESHEET = "assets/heart_spritesheet.png"


class Lives:
    """Renders the row of heart icons representing remaining lives."""

    def __init__(self, lives_count: int, mlx_ctx: MlxContext):
        """Load the heart sprites sized for the current window.

        Args:
            lives_count: Starting number of lives, used as the maximum
                number of heart icons drawn side by side.
            mlx_ctx: Window/rendering context used to size the icons.
        """
        self._max_lives = lives_count
        self._lives_count = lives_count
        self._mlx_ctx = mlx_ctx
        self.size = int(mlx_ctx.win_height * 0.07)
        self._assets = self._load_assets(self.size)

    def update(self, lives: int) -> None:
        """Update the number of remaining lives to display.

        Args:
            lives: Current number of lives.
        """
        self._lives_count = lives

    def get_width(self) -> int:
        """Return the pixel width needed to draw the current lives display.

        Returns:
            One icon's width if lives exceed the starting maximum (the
            "*N" overflow display is used instead), otherwise the width of
            the full row of heart icons.
        """
        if self._lives_count > self._max_lives:
            return self.size
        return self._max_lives * self.size

    def get_max_lives(self) -> int:
        """Return the starting number of lives (the icon row's capacity)."""
        return self._max_lives

    def render(
        self,
        main_screen: NDArray[np.uint8],
        x: int,
        y: int,
    ) -> None:
        """Draw the heart icon row (or a single icon when lives overflow).

        Args:
            main_screen: Destination pixel buffer to draw onto.
            x: X coordinate of the leftmost icon.
            y: Y coordinate of the icon row.
        """
        if self._lives_count > self._max_lives:
            FrameBuffer.draw_blended_tile(
                main_screen,
                self._assets[0],
                x,
                y,
            )
            return

        for i in range(self._max_lives):
            heart_image = 0 if i < self._lives_count else 1
            FrameBuffer.draw_blended_tile(
                main_screen,
                self._assets[heart_image],
                x + i * self.size,
                y,
            )

    def get_current_lives(self) -> int:
        """Return the number of lives currently displayed."""
        return self._lives_count

    def _load_assets(self, size: int) -> Tuple[NDArray[np.uint8],
                                               NDArray[np.uint8]]:
        """Load and dim the full/empty heart icons from the spritesheet.

        Args:
            size: Width and height in pixels to render each icon at.

        Returns:
            A (full_heart, empty_heart) pair of icon images.
        """
        spritesheet = FrameBuffer.get_image_array(_SPRITESHEET, size * 5,
                                                  size * 2)
        assets = spritesheet[:size, :size], spritesheet[:size, :size].copy()
        mask = FrameBuffer(self._mlx_ctx, size, size).get_array()
        mask[:, :] = [0, 0, 0, 178]
        FrameBuffer.draw_blended_tile(assets[1], mask, 0, 0)

        return assets
