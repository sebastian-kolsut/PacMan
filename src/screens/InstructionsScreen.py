import numpy as np

from src.models.dataclasses import MlxContext
from src.screens.draw_utils.FrameBuffer import FrameBuffer


_INSTRUCTIONS_IMAGE = "assets/menu/keyboard_controls.png"
_IMAGE_SCALE = 0.70


class InstructionsScreen:

    def __init__(self, mlx_ctx: MlxContext) -> None:
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )

        image_width = int(mlx_ctx.win_width * _IMAGE_SCALE)
        image_height = int(mlx_ctx.win_height * _IMAGE_SCALE)

        self._image = FrameBuffer.get_image_array(
            _INSTRUCTIONS_IMAGE,
            image_width,
            image_height,
        )

    def render(self) -> None:
        pixels = self._fb.get_array()
        pixels[:, :, :] = np.array([0, 0, 0, 255], dtype=np.uint8)

        x = (self._mlx_ctx.win_width - self._image.shape[1]) // 2
        y = (self._mlx_ctx.win_height - self._image.shape[0]) // 2

        FrameBuffer.draw_blended_tile(
            pixels,
            self._image,
            y,
            x,
        )

        self._fb.commit()
        self._fb.put_image_to_window()