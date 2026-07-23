from src.screens.draw_utils import FrameBuffer, RenderText
from src.models import MlxContext
from src.models.dataclasses import ProgramState, Screen

from numpy.typing import NDArray
import numpy as np


KEY_ESCAPE = 65307
KEY_ENTER = 65293

FONT_FILEPATH = "assets/fonts/gomarice_no_continue.ttf"
PAUSE_IMG_FILE = "assets/pause_sign_transparent.png"
_PAUSE_IMG_WIDTH = 2040
_PAUSE_IMG_HEIGHT = 780

KINDA_BLACK = (10, 0, 8, 255)
TRANSPARENT = (0, 0, 0, 0)
MAIN_TINT = (0, 0, 0, 220)


class PauseScreen:
    def __init__(self, mlx_ctx: MlxContext, game_state: ProgramState) -> None:
        self._mlx_ctx = mlx_ctx
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._txt = RenderText(FONT_FILEPATH, mlx_ctx, 0.1)
        self._img = self._fb.get_array()
        self._img[:, :] = np.array(MAIN_TINT, dtype=np.uint8)
        pause_width = int(mlx_ctx.win_width * 0.5)
        pause_height = int(pause_width * _PAUSE_IMG_HEIGHT / _PAUSE_IMG_WIDTH)
        self._img_pos_x = self._get_postion_x_centered(pause_width)
        self._img_pos_y = int(mlx_ctx.win_height * 0.1)
        self._pause_tile = self._fb.get_image_array(
            PAUSE_IMG_FILE, pause_width, pause_height)
        self._pause_tile = self._fb.swap_colors_in_image_color_to_color(
            KINDA_BLACK, TRANSPARENT, self._pause_tile
        )
        self._game_state = game_state
        self._is_paused = False

    def is_game_paused(self) -> bool:
        return self._is_paused

    def update(self, keycode: int) -> None:
        if self._is_paused and keycode == KEY_ENTER:
            self._is_paused = False
            return

        if keycode != KEY_ESCAPE:
            return

        if self._is_paused:
            self._is_paused = False
            self._game_state.screen = Screen.MAIN_MENU
        else:
            self._is_paused = True

    def render(self, image: NDArray[np.uint8]) -> None:
        self._img[:, :] = np.array(MAIN_TINT, dtype=np.uint8)
        self._fb.draw_blended_tile(self._img, self._pause_tile,
                                   self._img_pos_y, self._img_pos_x)
        self._put_text_to_img()

        self._fb.draw_blended_tile(image, self._img, 0, 0)

    def _put_text_to_img(self) -> None:
        con_txt = "continue (ENTER)"
        menu_txt = "back to main menu (ESC)"
        con = self._txt.put_text_to_image(con_txt)
        menu = self._txt.put_text_to_image(menu_txt)

        con_width = self._txt.get_text_width(con_txt)
        menu_width = self._txt.get_text_width(menu_txt)

        self._fb.draw_blended_tile(
            self._img, con, int(self._mlx_ctx.win_height * 0.60),
            self._get_postion_x_centered(con_width))
        self._fb.draw_blended_tile(
            self._img, menu, int(self._mlx_ctx.win_height * 0.75),
            self._get_postion_x_centered(menu_width))

    def _get_postion_x_centered(self, text_width: int):
        return (self._mlx_ctx.win_width // 2) - (text_width // 2)
