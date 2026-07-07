from src.models.dataclasses import GameState, MlxContext, Screen
from src.screens import PlayGame, MainMenu
from src.Parser import Parser
from mlx import Mlx  # type: ignore[import-untyped]
import time


_WASD = {119, 97, 115, 100}


class MainGameLoop:

    def __init__(self) -> None:
        self._config = Parser().parse("tests/jsons/valid_no_comments.json")
        self._state = GameState()
        self._mlx_ctx = self._init_mlx()
        self._main_menu_screen = MainMenu(self._mlx_ctx)
        self._game_screen = PlayGame(self._mlx_ctx, self._config)

    def run(self) -> None:
        self._mlx_ctx.m.mlx_loop(self._mlx_ctx.mlx_ptr)

    def game_loop(self, param) -> int:
        now = time.time()
        difference = now - self._state.last_frame_time

        if difference < self._state.frame_interval:
            time.sleep(difference)
        self._state.last_frame_time = time.time()

        # update() & render() for all
        match self._state.screen:
            case Screen.MAIN_MENU:
                self._main_menu_screen.render()
            case Screen.GAME_PLAYING:
                self._game_screen.update(difference)
                self._game_screen.render()
            case Screen.WIN_OR_LOSE:
                pass

        return 0

    def on_key(self, keycode: int, param) -> int:
        if keycode == 65307:  # Escape (X11 keysym)
            self._mlx_ctx.m.mlx_loop_exit(self._mlx_ctx.mlx_ptr)

        if keycode == 32 and self._state.screen == Screen.MAIN_MENU:  # Space
            self._state.screen = Screen.GAME_PLAYING

        if keycode in _WASD and self._state.screen == Screen.GAME_PLAYING:
            self._game_screen.handle_key_press(keycode)

        return 0

    def _init_mlx(self) -> MlxContext:
        m = Mlx()

        mlx_ptr = m.mlx_init()
        _, screen_width, screen_height = m.mlx_get_screen_size(mlx_ptr)

        win_width = min(2280, int(screen_width))
        win_height = min(1900, int(screen_height * 0.93))

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
