from src.screens.draw_utils import RenderText, FrameBuffer
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


_FPS_UPDATE_INTERVAL = 1.0


class Timer:
    def __init__(self, time_for_level: float, mlx_ctx: MlxContext) -> None:
        from .HUD import FONT_FILEPATH, FONT_SIZE

        self._time_left = time_for_level
        self._time_str = self._format_time()
        self._render_txt = RenderText(FONT_FILEPATH, mlx_ctx, FONT_SIZE)
        self._image = self._render_txt.put_text_to_image(self._time_str)
        self.fps = self._render_txt.put_text_to_image("0.00FPS")
        self._fps_timer = 0.0

    def reset(self, time_for_level: float) -> None:
        self._time_left = time_for_level

    def update(self, delta_time: float) -> bool:
        self._time_left -= delta_time

        self._fps_timer += delta_time
        if self._fps_timer >= _FPS_UPDATE_INTERVAL:
            self._fps_timer = 0.0
            self.fps = self._render_txt.put_text_to_image(
                f"{1 / delta_time:.2f}FPS")

        return self._time_left > 0

    def render_time(
        self,
        main_screen: NDArray[np.uint8],
        x: int,
        y: int,
    ) -> NDArray[np.uint8]:
        image = self.get_time_image()
        FrameBuffer.draw_blended_tile(main_screen, image, x, y)

        return image

    def get_time_image(self) -> NDArray[np.uint8]:
        new_time = self._format_time()
        if new_time != self._time_str:
            self._time_str = new_time
            self._image = self._render_txt.put_text_to_image(self._time_str)

        return self._image

    def render_fps(
        self,
        main_screen: NDArray[np.uint8],
        x: int,
        y: int,
    ) -> None:
        FrameBuffer.draw_blended_tile(main_screen, self.get_fps_image(), x, y)

    def get_fps_image(self) -> NDArray[np.uint8]:
        return self.fps

    def _format_time(self) -> str:
        now = int(round(self._time_left))
        minutes, seconds = divmod(now, 60)

        return f"{minutes:02d}:{seconds:02d}"
