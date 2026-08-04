from src.screens.draw_utils import RenderText, FrameBuffer
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


class Score:
    def __init__(self, mlx_ctx: MlxContext):
        from .HUD import FONT_FILEPATH, FONT_SIZE

        self._render_txt = RenderText(FONT_FILEPATH, mlx_ctx, FONT_SIZE)
        self._score = 0
        self._score_txt = str(self._score)
        self._dirty = False
        self._img = self._render_txt.put_text_to_image(self._score_txt)

    def update(self, points: int) -> None:
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
        image = self.get_image()
        FrameBuffer.draw_blended_tile(main_screen, image, x, y)

        return image

    def get_image(self) -> NDArray[np.uint8]:
        if self._dirty:
            self._img = self._render_txt.put_text_to_image(self._score_txt)
            self._dirty = False

        return self._img

    def get_score(self) -> int:
        return self._score
