import numpy as np
from numpy.typing import NDArray
from src.models.dataclasses import MlxContext


class FrameBuffer:
    def __init__(
            self, mlx_ctx: MlxContext, width: int, height: int):
        self._mlx_ctx = mlx_ctx
        self.img_ptr = mlx_ctx.m.mlx_new_image(mlx_ctx.mlx_ptr, width, height)
        data, bpp, size_line, img_format = \
            mlx_ctx.m.mlx_get_data_addr(self.img_ptr)

        self._data = data
        self._bpp = bpp
        self._size_line = size_line
        self._img_format = img_format
        self._bytes_per_pixel = bpp // 8
        self.height = height
        self.width = width

        self._frame = np.zeros((height, size_line), dtype=np.uint8)

    @staticmethod
    def draw_blended_tile(
            pixels,
            tile: NDArray[np.uint8],
            y0: int,
            x0: int) -> None:
        tile_h, tile_w = tile.shape[0], tile.shape[1]
        y1, x1 = y0 + tile_h, x0 + tile_w

        if y1 > pixels.shape[0] or x1 > \
                pixels.shape[1] or y0 < 0 or x0 < 0:
            raise ValueError(
                f"Tile at ({x0}, {y0}) of size ({tile_w}, {tile_h}) "
                f"does not fit in pixel buffer of shape {pixels.shape}"
            )

        alpha = tile[:, :, 3:4].astype(np.float32) / 255.0
        background = pixels[y0:y1, x0:x1, :3].astype(np.float32)
        foreground = tile[:, :, :3].astype(np.float32)

        blended = foreground * alpha + background * (1.0 - alpha)

        pixels[y0:y1, x0:x1, :3] = blended.astype(np.uint8)
        pixels[y0:y1, x0:x1, 3] = 255

    def get_array(self) -> np.ndarray:
        return self._frame[:, :self.width * self._bytes_per_pixel].reshape(
            self.height, self.width, self._bytes_per_pixel
        )

    def commit(self) -> None:
        self._data[:] = self._frame.tobytes()
