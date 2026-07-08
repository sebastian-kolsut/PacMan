from PIL import Image, ImageFont, ImageDraw
from typing import Dict, Tuple
from .FrameBuffer import FrameBuffer
from numpy.typing import NDArray
import numpy as np

from src.models import MlxContext


_ASCII_RANGE = (32, 126)

_WHITE = (255, 255, 255)


class RenderFont:
    def __init__(self, font_file: str, mlx_ctx: MlxContext) -> None:
        self._font_size = int(mlx_ctx.win_height * 0.03)
        self._font_images, self._char_widths = \
            self._load_font_images(font_file)
        self._mlx_ctx = mlx_ctx

    def put_text_to_image(self, text: str):
        self._fb = FrameBuffer(
            self._mlx_ctx, self._font_size * len(text),
            self._font_size)
        image = self._fb.get_array()

        x_pos = 0
        for char in text:
            self._fb.draw_blended_tile(image, self._font_images[char],
                                       0, x_pos)
            x_pos += int(self._char_widths[char])

        return image

    def _load_font_images(
            self, font_file: str
    ) -> Tuple[Dict[str, NDArray[np.uint8]], Dict[str, int]]:
        self.font = ImageFont.truetype(font_file, self._font_size)
        ascii: Dict[str, NDArray[np.uint8]] = {}
        widths: Dict[str, int] = {}

        for i in range(*_ASCII_RANGE):
            char = chr(i)

            mask = Image.new("L", (self._font_size, self._font_size), 0)
            draw = ImageDraw.Draw(mask)

            bbox = self.font.getbbox(char)
            left_offset = bbox[0]

            x_pos = 0 - left_offset
            y_pos = 0

            draw.text((x_pos, y_pos), char, fill=255, font=self.font)

            rgb_base = Image.new("RGB", (self._font_size, self._font_size),
                                 color=_WHITE)
            rgba_image = rgb_base.copy()
            rgba_image.putalpha(mask)

            ascii[char] = np.array(rgba_image, dtype=np.uint8)
            widths[char] = max(1, round(self.font.getlength(char)))

        return ascii, widths
