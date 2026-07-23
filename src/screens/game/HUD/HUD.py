from .Timer import Timer
from .Lives import Lives
from .Score import Score
from src.models import Config, MlxContext

from numpy.typing import NDArray
import numpy as np


FONT_FILEPATH = "assets/fonts/gomarice_no_continue.ttf"
FONT_SIZE = 0.05


class HUD:
    def __init__(self, config: Config, mlx_ctx: MlxContext):
        self._timer = Timer(config.level_max_time, mlx_ctx)
        self._lives = Lives(config.lives, mlx_ctx)
        self._score = Score(mlx_ctx)

    def update(self, delta_time: float, points: int, lives: int) -> bool:
        self._score.update(points)
        self._lives.update(lives)
        if not self._timer.update(delta_time):
            return False
        return True

    def render(self, main_screen_img: NDArray[np.uint8]) -> None:
        self._timer.render(main_screen_img)
        self._lives.render(main_screen_img)
        self._score.render(main_screen_img)
