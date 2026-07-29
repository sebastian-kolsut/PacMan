from src.screens.draw_utils import FrameBuffer, RenderText
from src.Highscores import Highscores
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


_LABEL_FILE = "assets/menu/highscores_marquee.png"

_Y = 0.38


class HighscoresScreen:
    def __init__(self, file_name: str, mlx_ctx: MlxContext):
        self._scores = Highscores(file_name)
        self._render_txt = RenderText("assets/fonts/ByteBounce.ttf",
                                      mlx_ctx, 0.07)
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._mlx_ctx = mlx_ctx
        self._label_img = self._fb.get_image_array(
            _LABEL_FILE, mlx_ctx.win_width, mlx_ctx.win_height)

    def render(self) -> None:
        frame = self._fb.get_array()
        frame[:, :] = np.array([0, 0, 0, 255], dtype=np.uint8)

        self._fb.draw_blended_tile(frame, self._label_img, 0, 0)
        self._put_text_to_image(frame)

        self._fb.commit()
        self._fb.put_image_to_window()

    def _put_text_to_image(self, frame: NDArray[np.uint8]) -> None:
        leaderboard = self._scores.get_leaderboard()

        x = self._mlx_ctx.win_width // 2 \
            - self._render_txt.get_text_width(leaderboard[1]) // 2
        y = int(self._mlx_ctx.win_height * _Y)

        height = self._render_txt.get_text_height()
        for record in leaderboard:
            img = self._render_txt.put_text_to_image(record)
            if record.startswith("1."):
                self._fb.draw_blended_tile(frame, img, y, x +
                                           self._get_diffrence_for_one())
            else:
                self._fb.draw_blended_tile(frame, img, y, x)
            y += height

    def _get_diffrence_for_one(self) -> int:
        return self._render_txt.get_text_width("2") - \
            self._render_txt.get_text_width("1")
