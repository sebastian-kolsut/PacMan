from src.screens.draw_utils import FrameBuffer
from src.models import MlxContext

from typing import Tuple
from numpy.typing import NDArray
import numpy as np


_SPRITESHEET = "assets/heart_spritesheet.png"


class Lives:
    def __init__(self, lives_count: int, mlx_ctx: MlxContext):
        self._lives_count = lives_count
        self._mlx_ctx = mlx_ctx
        self.size = int(mlx_ctx.win_height * 0.07)
        self._assets = self._load_assets(self.size)

    def render(self, main_screen: NDArray[np.uint8]) -> None:
        for i in range(3):
            FrameBuffer.draw_blended_tile(
                main_screen, self._assets[i % 2], 20,
                int(self._mlx_ctx.win_width * 0.8) + i * self.size)

    def _load_assets(self, size: int) -> Tuple[NDArray[np.uint8],
                                               NDArray[np.uint8]]:
        spritesheet = FrameBuffer.get_image_array(_SPRITESHEET, size * 5,
                                                  size * 2)
        assets = spritesheet[:size, :size], spritesheet[:size, :size].copy()
        mask = FrameBuffer(self._mlx_ctx, size, size).get_array()
        mask[:, :] = [0, 0, 0, 128]
        FrameBuffer.draw_blended_tile(assets[1], mask, 0, 0)

        return assets
