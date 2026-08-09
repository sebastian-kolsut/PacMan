from .Timer import Timer
from .Lives import Lives
from .Score import Score
from src.models import Config, MlxContext
from src.screens.draw_utils import FrameBuffer

from numpy.typing import NDArray
import numpy as np


FONT_FILEPATH = "assets/fonts/gomarice_no_continue.ttf"
FONT_SIZE = 0.05

_TIME_LEFT_LABEL = "assets/hud/time_left_label.png"
_SCORE_LABEL = "assets/hud/score_label.png"
_LIFE_LEFT_LABEL = "assets/hud/life_left_label_gold.png"
_LABEL_WIDTH = 410
_LABEL_HEIGHT = 155
_LABEL_WIDTH_SCALE = 0.12


class HUD:
    def __init__(self, config: Config, mlx_ctx: MlxContext):
        self._mlx_ctx = mlx_ctx
        self._timer = Timer(config.levels[0].level_max_time, mlx_ctx)
        self._lives = Lives(config.lives, mlx_ctx)
        self._score = Score(mlx_ctx)
        self._label_width = int(mlx_ctx.win_width * _LABEL_WIDTH_SCALE)
        self._label_height = int(
            self._label_width * _LABEL_HEIGHT / _LABEL_WIDTH
        )
        self._time_left_label = FrameBuffer.get_image_array(
            _TIME_LEFT_LABEL,
            self._label_width,
            self._label_height,
        )
        self._score_label = FrameBuffer.get_image_array(
            _SCORE_LABEL,
            self._label_width,
            self._label_height,
        )
        self._life_left_label = FrameBuffer.get_image_array(
            _LIFE_LEFT_LABEL,
            self._label_width,
            self._label_height,
        )
        self._margin = max(20, int(mlx_ctx.win_height * 0.03))
        self._gap = max(8, int(mlx_ctx.win_height * 0.01))
        self._maze_left = 0
        self._maze_right = mlx_ctx.win_width

    def set_maze_bounds(self, maze_left: int, maze_width: int) -> None:
        self._maze_left = maze_left
        self._maze_right = maze_left + maze_width

    def reset_timer(self, time_for_level: float) -> None:
        self._timer.reset(time_for_level)

    def get_score(self) -> int:
        return self._score.get_score()

    def update(self, delta_time: float, points: int, lives: int) -> bool:
        self._score.update(points)
        self._lives.update(lives)
        if not self._timer.update(delta_time):
            return False
        return True

    def render(self, main_screen_img: NDArray[np.uint8]) -> None:
        left_label_x = (self._maze_left - self._label_width) // 2
        time_label_y = self._margin
        FrameBuffer.draw_blended_tile(
            main_screen_img,
            self._time_left_label,
            left_label_x,
            time_label_y,
        )
        time_y = time_label_y + self._label_height + self._gap
        time_image = self._timer.get_time_image()
        time_x = left_label_x + (self._label_width - time_image.shape[1]) // 2
        self._timer.render_time(main_screen_img, time_x, time_y)

        score_label_y = time_y + time_image.shape[0] + self._gap
        FrameBuffer.draw_blended_tile(
            main_screen_img,
            self._score_label,
            left_label_x,
            score_label_y,
        )
        score_y = score_label_y + self._label_height + self._gap
        score_image = self._score.get_image()
        score_x = left_label_x + (self._label_width - score_image.shape[1]) // 2
        self._score.render(main_screen_img, score_x, score_y)

        fps_y = score_y + score_image.shape[0] + self._gap
        fps_image = self._timer.get_fps_image()
        fps_x = left_label_x + (self._label_width - fps_image.shape[1]) // 2
        self._timer.render_fps(main_screen_img, fps_x, fps_y)

        lives_label_x = (
            self._maze_right + (
                self._mlx_ctx.win_width - self._maze_right - self._label_width
            ) // 2
        )
        lives_label_y = self._margin
        FrameBuffer.draw_blended_tile(
            main_screen_img,
            self._life_left_label,
            lives_label_x,
            lives_label_y,
        )
        lives_y = lives_label_y + self._label_height + self._gap
        lives_x = lives_label_x + (
            self._label_width - self._lives.get_width()
        ) // 2
        self._lives.render(main_screen_img, lives_x, lives_y)
