import numpy as np

from src.models.dataclasses import MlxContext, ProgramState, GameState
from src.screens.draw_utils.FrameBuffer import FrameBuffer


_GAME_OVER_IMAGE = "assets/menu/gameover.png"
_YOU_WON_IMAGE = "assets/menu/you_won.png"


class WinLoseScreen:
    def __init__(self, mlx_ctx: MlxContext, state: ProgramState) -> None:
        self._mlx_ctx = mlx_ctx
        self._state = state
        self._fb = FrameBuffer(
            mlx_ctx,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )
        self._img_game_over = FrameBuffer.get_image_array(
            _GAME_OVER_IMAGE,
            mlx_ctx.win_width,
            mlx_ctx.win_height,
        )
        self._img_you_won = FrameBuffer.get_image_array(
                    _YOU_WON_IMAGE,
                    mlx_ctx.win_width,
                    mlx_ctx.win_height,
                )

    def render(self) -> None:
        pixels = self._fb.get_array()
        pixels[:, :, :] = np.array([0, 0, 0, 255], dtype=np.uint8)

        img = self._img_you_won if self._state.state == GameState.WON \
            else self._img_game_over

        FrameBuffer.draw_blended_tile(pixels, img, 0, 0)

        self._fb.commit()
        self._fb.put_image_to_window()
