from src.screens.draw_utils import RenderText, FrameBuffer
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


_FONT_FILEPATH = "assets/fonts/gomarice_no_continue.ttf"
_FONT_SIZE = 0.05

_FPS_UPDATE_INTERVAL = 1.0


class Timer:
    def __init__(self, time_for_level: float, mlx_ctx: MlxContext) -> None:
        self._time_left = time_for_level
        self._time_str = self._format_time()
        self._render_txt = RenderText(_FONT_FILEPATH, mlx_ctx, _FONT_SIZE)
        self._image = self._render_txt.put_text_to_image(self._time_str)
        self.fps = self._render_txt.put_text_to_image("0.00FPS")
        self._fps_timer = 0.0

    def update(self, delta_time: float) -> bool:
        self._time_left -= delta_time

        self._fps_timer += delta_time
        if self._fps_timer >= _FPS_UPDATE_INTERVAL:
            self._fps_timer = 0.0
            self.fps = self._render_txt.put_text_to_image(
                f"{1 / delta_time:.2f}FPS")

        return self._time_left > 0

    def render(self, main_screen: NDArray[np.uint8]) -> NDArray[np.uint8]:
        new_time = self._format_time()
        if new_time != self._time_str:
            self._time_str = new_time
            self._image = self._render_txt.put_text_to_image(self._time_str)

        FrameBuffer.draw_blended_tile(main_screen, self._image, 20, 20)
        FrameBuffer.draw_blended_tile(main_screen, self.fps, 80, 20)

        return self._image

    def _format_time(self) -> str:
        now = int(round(self._time_left))
        minutes, seconds = divmod(now, 60)

        return f"Time left: {minutes:02d}:{seconds:02d}"
