from src.models.dataclasses import GameState, MlxContext, Screen
from src.Parser import Parser
from mlx import Mlx  # type: ignore[import-untyped]
from src.screens import PlayGame
import time


class MainGameLoop:

    def __init__(self) -> None:
        self._config = Parser().parse("tests/jsons/valid_no_comments.json")
        self._state = GameState()
        self._mlx_ctx = self._init_mlx()
        self._game_screen = PlayGame(self._mlx_ctx, self._config)

    def run(self) -> None:
        self._mlx_ctx.m.mlx_loop(self._mlx_ctx.mlx_ptr)

    def game_loop(self, param) -> int:
        now = time.time()

        self._state.screen = Screen.GAME_PLAYING
        if now - self._state.last_frame_time < self._state.frame_interval:
            return 0
        # update() & render() for all
        match self._state.screen:
            case Screen.MAIN_MENU:
                pass
            case Screen.GAME_PLAYING:
                self._game_screen.render()
            case Screen.WIN_OR_LOSE:
                pass
        return 0

    def on_key(self, keycode: int, param) -> int:
        if keycode == 65307:  # Escape (X11 keysym)
            self._mlx_ctx.m.mlx_loop_exit(self._mlx_ctx.mlx_ptr)
        return 0

    def _init_mlx(self) -> MlxContext:
        m = Mlx()

        mlx_ptr = m.mlx_init()
        win_width, win_height = m.mlx_get_screen_size(mlx_ptr)[1:]
        win_height = int(win_height * 0.93)
        win_ptr = m.mlx_new_window(mlx_ptr, win_width, win_height, "PacMan")

        mlx_ctx = MlxContext(
            m=m,
            mlx_ptr=mlx_ptr,
            win_ptr=win_ptr,
            win_width=win_width,
            win_height=win_height
            )
        mlx_ctx.m.mlx_loop_hook(
            mlx_ctx.mlx_ptr, self.game_loop, None)
        mlx_ctx.m.mlx_key_hook(win_ptr, self.on_key, None)

        return mlx_ctx
