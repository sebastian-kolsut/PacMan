import numpy as np

from src.models.dataclasses import MlxContext
from src.screens.draw_utils.FrameBuffer import FrameBuffer


_GAME_OVER_IMAGE = "assets/menu/gameover.png"


class LoseScreen:
    def __init__(self, mlx_ctx: MlxContext) -> None:
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )
        self._image = FrameBuffer.get_image_array(
            _GAME_OVER_IMAGE,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )

    def render(self) -> None:
        pixels = self._fb.get_array()
        pixels[:, :, :] = np.array([0, 0, 0, 255], dtype=np.uint8)

        FrameBuffer.draw_blended_tile(
            pixels,
            self._image,
            0,
            0,
        )

        self._fb.commit()
        self._fb.put_image_to_window()