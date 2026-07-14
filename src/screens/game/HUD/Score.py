from src.screens.draw_utils import RenderText, FrameBuffer
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


class Score:
    def __init__(self, mlx_ctx: MlxContext):
        from .HUD import FONT_FILEPATH, FONT_SIZE

        self._render_txt = RenderText(FONT_FILEPATH, mlx_ctx, FONT_SIZE)
        self._score = 0
        self._score_txt = f"SCORE: {self._score}"
        self._dirty = False
        self._img = self._render_txt.put_text_to_image(self._score_txt)

    def update(self, points: int):
        self._score += points
        self._score_txt = f"SCORE: {self._score}"
        self._dirty = False

    def render(self, main_screen: NDArray[np.uint8]) -> None:
        if self._dirty:
            FrameBuffer.draw_blended_tile(main_screen, self._img, 150, 20)
            return

        self._img = self._render_txt.put_text_to_image(self._score_txt)
        FrameBuffer.draw_blended_tile(main_screen, self._img, 150, 20)
