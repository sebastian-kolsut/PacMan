import numpy as np
from numpy.typing import NDArray
from typing import Tuple
from src.models.dataclasses import MlxContext
from PIL import Image


class FrameBuffer:
    """An MLX off-screen image plus pixel-blending/loading utilities."""

    def __init__(
            self, mlx_ctx: MlxContext, width: int, height: int):
        """Allocate an MLX image and expose it as a numpy pixel buffer.

        Args:
            mlx_ctx: Window/rendering context that owns the MLX image.
            width: Width of the image in pixels.
            height: Height of the image in pixels.
        """
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
        """Blit this buffer's committed image onto the game window."""
        self._mlx_ctx.m.mlx_put_image_to_window(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            self.img_ptr, 0, 0
        )

    @staticmethod
    def draw_blended_tile(
            pixels: NDArray[np.uint8],
            tile: NDArray[np.uint8],
            x0: int,
            y0: int) -> None:
        """Alpha-blend tile onto pixels at (x0, y0), clipped to bounds.

        Whatever part of tile would fall outside pixels is silently
        cropped rather than raising, so callers do not need to
        pre-validate positions or sizes for content that can grow at
        runtime (e.g. score text, cheat-code text).

        Args:
            pixels: Destination RGBA pixel buffer to blend onto.
            tile: Source RGBA image to blend in.
            x0: X coordinate to place the tile's top-left corner at.
            y0: Y coordinate to place the tile's top-left corner at.
        """
        tile_h, tile_w = tile.shape[0], tile.shape[1]
        y1, x1 = y0 + tile_h, x0 + tile_w

        clip_x0, clip_y0 = max(x0, 0), max(y0, 0)
        clip_x1 = min(x1, pixels.shape[1])
        clip_y1 = min(y1, pixels.shape[0])

        if clip_x1 <= clip_x0 or clip_y1 <= clip_y0:
            return

        if (clip_x0, clip_y0, clip_x1, clip_y1) != (x0, y0, x1, y1):
            tile = tile[
                clip_y0 - y0:clip_y1 - y0,
                clip_x0 - x0:clip_x1 - x0,
            ]
            x0, y0, x1, y1 = clip_x0, clip_y0, clip_x1, clip_y1

        alpha = tile[:, :, 3:4].astype(np.float32) / 255.0
        background = pixels[y0:y1, x0:x1, :3].astype(np.float32)
        background_alpha = pixels[y0:y1, x0:x1, 3:4].astype(np.float32) / 255.0
        foreground = tile[:, :, :3].astype(np.float32)

        blended = foreground * alpha + background * (1.0 - alpha)
        out_alpha = alpha + background_alpha * (1.0 - alpha)

        pixels[y0:y1, x0:x1, :3] = blended.astype(np.uint8)
        pixels[y0:y1, x0:x1, 3:] = (out_alpha * 255.0).astype(np.uint8)

    @staticmethod
    def draw_clipped(
            pixels: NDArray[np.uint8],
            tile: NDArray[np.uint8],
            x0: int,
            y0: int) -> None:
        """Copy tile onto pixels at (x0, y0), cropped to whatever overlaps.

        Unlike draw_blended_tile, this performs a plain (non-blended)
        channel copy, matching the direct numpy slice assignment this
        replaces for the maze, side-character and pacgum sprites.

        Args:
            pixels: Destination pixel buffer to copy onto.
            tile: Source image to copy in.
            x0: X coordinate to place the tile's top-left corner at.
            y0: Y coordinate to place the tile's top-left corner at.
        """
        tile_h, tile_w = tile.shape[0], tile.shape[1]
        y1, x1 = y0 + tile_h, x0 + tile_w

        clip_x0, clip_y0 = max(x0, 0), max(y0, 0)
        clip_x1 = min(x1, pixels.shape[1])
        clip_y1 = min(y1, pixels.shape[0])

        if clip_x1 <= clip_x0 or clip_y1 <= clip_y0:
            return

        tile_slice = tile[
            clip_y0 - y0:clip_y1 - y0,
            clip_x0 - x0:clip_x1 - x0,
        ]
        channels = tile_slice.shape[2]
        pixels[clip_y0:clip_y1, clip_x0:clip_x1, :channels] = tile_slice

    def get_array(self) -> NDArray[np.uint8]:
        """Return this buffer's pixels as an (height, width, channels) array.

        Returns:
            A view onto the underlying pixel buffer, sized to this
            FrameBuffer's actual width and height (excluding row padding).
        """
        return self._frame[:, :self.width * self._bytes_per_pixel].reshape(
            self.height, self.width, self._bytes_per_pixel
        )

    def commit(self) -> None:
        """Flush the numpy pixel buffer into the underlying MLX image."""
        self._data[:] = self._frame.tobytes()

    def get_frame(self) -> NDArray[np.uint8]:
        """Return the raw (height, padded-width) pixel buffer."""
        return self._frame

    @staticmethod
    def swap_colors_in_image_leave_out(
            color_to_leave_out_bgra: Tuple[int, int, int, int],
            new_color_bgra: Tuple[int, int, int, int],
            image: NDArray[np.uint8]) -> NDArray[np.uint8]:
        """Recolor every pixel except a given color.

        Args:
            color_to_leave_out_bgra: BGRA color that must stay unchanged.
            new_color_bgra: BGRA color applied to all other pixels.
            image: Source image to recolor.

        Returns:
            A new image with the recoloring applied.
        """
        new_image = np.array(image)
        mask = ~np.all(new_image == [*color_to_leave_out_bgra], axis=-1)

        new_image[mask] = [*new_color_bgra]

        return new_image

    @staticmethod
    def swap_colors_in_image_color_to_color(
            old_color_bgra: Tuple[int, int, int, int],
            new_color_bgra: Tuple[int, int, int, int],
            image: NDArray[np.uint8]) -> NDArray[np.uint8]:
        """Replace one exact color with another throughout an image.

        Args:
            old_color_bgra: BGRA color to replace.
            new_color_bgra: BGRA color to replace it with.
            image: Source image to recolor.

        Returns:
            A new image with the recoloring applied.
        """
        new_image = np.array(image)
        mask = np.all(new_image == [*old_color_bgra], axis=-1)

        new_image[mask] = [*new_color_bgra]

        return new_image

    @staticmethod
    def get_image_array(file_name: str, width: int,
                        height: int) -> NDArray[np.uint8]:
        """Load an image file and resize it to a BGRA numpy array.

        Args:
            file_name: Path to the image file to load.
            width: Target width in pixels.
            height: Target height in pixels.

        Returns:
            The resized image as a BGRA (height, width, 4) array.
        """
        img = Image.open(file_name).convert("RGBA")
        r, g, b, a = img.split()
        img_bgra = Image.merge("RGBA", (b, g, r, a))
        resized = img_bgra.resize(
            (width, height),
            Image.Resampling.NEAREST
            )

        return np.array(resized)
