from src.dataclasses import GameState, MlxContext, Screen
from mlx import Mlx  # type: ignore[import-untyped]
import time


class MainGameLoop:

    def __init__(self) -> None:
        self._state = GameState()
        m = Mlx()

        mlx_ptr = m.mlx_init()
        win_size = m.mlx_get_screen_size(mlx_ptr)[1:]
        win_ptr = m.mlx_new_window(mlx_ptr, win_size[0], win_size[1], "PacMan")

        self._mlx = MlxContext(
            m=m,
            mlx_ptr=mlx_ptr,
            win_ptr=win_ptr
            )
        self._mlx.m.mlx_loop_hook(self._mlx.mlx_ptr, self.game_loop, None)

    def run(self) -> None:
        self._mlx.m.mlx_loop(self._mlx.mlx_ptr)

    def game_loop(self, param) -> int:
        now = time.time()

        if now - self._state.last_frame_time < self._state.frame_interval:
            return 0
        # update() & render() for all
        match self._state.screen:
            case Screen.MAIN_MENU:
                pass
            case Screen.GAME_PLAYING:
                pass
            case Screen.WIN_OR_LOSE:
                pass
        return 0
