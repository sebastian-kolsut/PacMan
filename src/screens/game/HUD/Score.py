from src.screens.draw_utils import RenderText, FrameBuffer
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


class Score:
    """Tracks and renders the player's current score as an image."""

    def __init__(self, mlx_ctx: MlxContext):
        """Initialize the score at zero and render its first image.

        Args:
            mlx_ctx: Window/rendering context used to size the score text.
        """
        from .HUD import FONT_FILEPATH, FONT_SIZE

        self._render_txt = RenderText(FONT_FILEPATH, mlx_ctx, FONT_SIZE)
        self._score = 0
        self._score_txt = str(self._score)
        self._dirty = False
        self._img = self._render_txt.put_text_to_image(self._score_txt)

    def update(self, points: int) -> None:
        """Add points to the running score.

        Args:
            points: Points earned this frame (may be zero).
        """
        if points == 0:
            return

        self._score += points
        self._score_txt = str(self._score)
        self._dirty = True

    def render(
        self,
        main_screen: NDArray[np.uint8],
        x: int,
        y: int,
    ) -> NDArray[np.uint8]:
        """Draw the current score onto main_screen.

        Args:
            main_screen: Destination pixel buffer to draw onto.
            x: X coordinate to draw the score text at.
            y: Y coordinate to draw the score text at.

        Returns:
            The rendered score text image.
        """
        image = self.get_image()
        FrameBuffer.draw_blended_tile(main_screen, image, x, y)

        return image

    def get_image(self) -> NDArray[np.uint8]:
        """Return the current score's text image, re-rendering if stale.

        Returns:
            The score text image, up to date with the latest score.
        """
        if self._dirty:
            self._img = self._render_txt.put_text_to_image(self._score_txt)
            self._dirty = False

        return self._img

    def get_score(self) -> int:
        """Return the current numeric score."""
        return self._score
