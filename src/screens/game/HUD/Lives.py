from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext

from typing import Tuple
from numpy.typing import NDArray
import numpy as np


_SPRITESHEET = "assets/heart_spritesheet.png"


class Lives:
    def __init__(self, lives_count: int, mlx_ctx: MlxContext):
        self._max_lives = lives_count
        self._lives_count = lives_count
        self._mlx_ctx = mlx_ctx
        self.size = int(mlx_ctx.win_height * 0.07)
        self._assets = self._load_assets(self.size)

    def update(self, lives: int) -> None:
        self._lives_count = lives

    def get_width(self) -> int:
        if self._lives_count > self._max_lives:
            return self.size
        return self._max_lives * self.size

    def get_max_lives(self) -> int:
        return self._max_lives

    def render(
        self,
        main_screen: NDArray[np.uint8],
        x: int,
        y: int,
    ) -> None:
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
        return self._lives_count

    def _load_assets(self, size: int) -> Tuple[NDArray[np.uint8],
                                               NDArray[np.uint8]]:
        spritesheet = FrameBuffer.get_image_array(_SPRITESHEET, size * 5,
                                                  size * 2)
        assets = spritesheet[:size, :size], spritesheet[:size, :size].copy()
        mask = FrameBuffer(self._mlx_ctx, size, size).get_array()
        mask[:, :] = [0, 0, 0, 178]
        FrameBuffer.draw_blended_tile(assets[1], mask, 0, 0)

        return assets
