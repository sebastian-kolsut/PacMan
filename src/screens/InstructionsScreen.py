import numpy as np

from src.models.dataclasses import MlxContext
from src.screens.draw_utils.FrameBuffer import FrameBuffer


_CONTROLS_IMAGE = "assets/menu/controls.png"
_GUIDE_IMAGE = "assets/menu/guide.png"
_IMAGE_MAX_WIDTH_SCALE = 0.90
_IMAGE_MAX_HEIGHT_SCALE = 0.90

KEY_ESCAPE = 65307
KEY_LEFT = 65361
KEY_RIGHT = 65363
KEY_A = 97
KEY_D = 100


class InstructionsScreen:

    def __init__(self, mlx_ctx: MlxContext) -> None:
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )
        self._page_index = 0
        page_width, page_height = self._calculate_page_size()
        self._pages = [
            FrameBuffer.get_image_array(
                _CONTROLS_IMAGE,
                page_width,
                page_height,
            ),
            FrameBuffer.get_image_array(
                _GUIDE_IMAGE,
                page_width,
                page_height,
            ),
        ]

    def handle_key(self, keycode: int) -> str | None:
        if keycode == KEY_ESCAPE:
            return "main_menu"
        if keycode in (KEY_LEFT, KEY_A):
            self._page_index = max(0, self._page_index - 1)
            return None
        if keycode in (KEY_RIGHT, KEY_D):
            self._page_index = min(len(self._pages) - 1, self._page_index + 1)
            return None
        return None

    def reset(self) -> None:
        self._page_index = 0

    def _calculate_page_size(self) -> tuple[int, int]:
        max_width = int(self._mlx_ctx.win_width * _IMAGE_MAX_WIDTH_SCALE)
        max_height = int(self._mlx_ctx.win_height * _IMAGE_MAX_HEIGHT_SCALE)
        width = min(
            max_width,
            int(max_height * self._get_page_aspect_ratio()),
        )
        height = int(width / self._get_page_aspect_ratio())

        return max(1, width), max(1, height)

    def _get_page_aspect_ratio(self) -> float:
        return 1536 / 1024

    def render(self) -> None:
        pixels = self._fb.get_array()
        pixels[:, :, :] = np.array([0, 0, 0, 255], dtype=np.uint8)
        page = self._pages[self._page_index]
        x = (self._mlx_ctx.win_width - page.shape[1]) // 2
        y = (self._mlx_ctx.win_height - page.shape[0]) // 2

        FrameBuffer.draw_blended_tile(
            pixels,
            page,
            x,
            y,
        )

        self._fb.commit()
        self._fb.put_image_to_window()
