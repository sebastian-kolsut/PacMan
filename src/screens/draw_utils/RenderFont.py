from PIL import Image, ImageFont, ImageDraw
from typing import Dict, Tuple
from .FrameBuffer import FrameBuffer
from numpy.typing import NDArray
import numpy as np

from src.models import MlxContext


_ASCII_RANGE = (32, 126)

_WHITE = (255, 255, 255)


class RenderFont:
    def __init__(self, font_file: str, mlx_ctx: MlxContext,
                 font_scale: float) -> None:
        self._font_size = int(mlx_ctx.win_height * font_scale)
        self._font_images, self._char_widths = \
            self._load_font_images(font_file)
        self._mlx_ctx = mlx_ctx

    def put_text_to_image(self, text: str):
        self._fb = FrameBuffer(
            self._mlx_ctx, self._get_text_width(text),
            self._font_height)
        image = self._fb.get_array()

        x_pos = 0
        for char in text:
            self._fb.draw_blended_tile(image, self._font_images[char],
                                       0, x_pos)
            x_pos += int(self._char_widths[char])

        return image

    def _get_text_width(self, text: str) -> int:
        len = 0

        for char in text:
            len += self._char_widths[char]

        return len

    def _load_font_images(
            self, font_file: str
    ) -> Tuple[Dict[str, NDArray[np.uint8]], Dict[str, int]]:
        self.font = ImageFont.truetype(font_file, self._font_size)
        ascii: Dict[str, NDArray[np.uint8]] = {}
        widths: Dict[str, int] = {}

        ascent, descent = self.font.getmetrics()

        bboxes = {}
        min_top = 0
        max_bottom = ascent + descent
        for i in range(*_ASCII_RANGE):
            char = chr(i)
            bbox = self.font.getbbox(char)
            bboxes[char] = bbox
            min_top = min(min_top, bbox[1])
            max_bottom = max(max_bottom, bbox[3])

        font_max_height = max_bottom - min_top
        self._font_height = max_bottom - min_top
        y_pos = 0 - min_top

        for i in range(*_ASCII_RANGE):
            char = chr(i)

            char_width = int(max(1, round(self.font.getlength(char))))

            mask = Image.new("L", (char_width, font_max_height), 0)
            draw = ImageDraw.Draw(mask)

            bbox = bboxes[char]
            left_offset = bbox[0]

            x_pos = 0 - left_offset

            draw.text((x_pos, y_pos), char, fill=255, font=self.font)

            rgb_base = Image.new("RGB", (char_width, font_max_height),
                                 color=_WHITE)
            rgba_image = rgb_base.copy()
            rgba_image.putalpha(mask)

            ascii[char] = np.array(rgba_image, dtype=np.uint8)
            widths[char] = char_width

        return ascii, widths
