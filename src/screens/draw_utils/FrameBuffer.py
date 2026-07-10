import numpy as np
from numpy.typing import NDArray
from typing import Tuple
from src.models.dataclasses import MlxContext
from PIL import Image


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

    def put_image_to_window(self) -> None:
        self._mlx_ctx.m.mlx_put_image_to_window(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            self.img_ptr, 0, 0
        )

    @staticmethod
    def draw_blended_tile(
            pixels: NDArray[np.uint8],
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

    def get_array(self) -> NDArray[np.uint8]:
        return self._frame[:, :self.width * self._bytes_per_pixel].reshape(
            self.height, self.width, self._bytes_per_pixel
        )

    def commit(self) -> None:
        self._data[:] = self._frame.tobytes()

    def get_frame(self):
        return self._frame

    @staticmethod
    def swap_colors_in_image_leave_out(
            color_to_leave_out_bgra: Tuple[int, int, int, int],
            new_color_bgra: Tuple[int, int, int, int],
            image: NDArray[np.uint8]) -> NDArray[np.uint8]:
        new_image = np.array(image)
        mask = ~np.all(new_image == [*color_to_leave_out_bgra], axis=-1)

        new_image[mask] = [*new_color_bgra]

        return new_image

    @staticmethod
    def swap_colors_in_image_color_to_color(
            old_color_bgra: Tuple[int, int, int, int],
            new_color_bgra: Tuple[int, int, int, int],
            image: NDArray[np.uint8]) -> NDArray[np.uint8]:
        new_image = np.array(image)
        mask = np.all(new_image == [*old_color_bgra], axis=-1)

        new_image[mask] = [*new_color_bgra]

        return new_image

    @staticmethod
    def get_image_array(file_name: str, width: int,
                        height: int) -> NDArray[np.uint8]:
        img = Image.open(file_name).convert("RGBA")
        r, g, b, a = img.split()
        img_bgra = Image.merge("RGBA", (b, g, r, a))
        resized = img_bgra.resize(
            (width, height),
            Image.Resampling.NEAREST
            )

        return np.array(resized)
