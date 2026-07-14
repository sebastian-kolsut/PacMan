from src.models.dataclasses import GameState, MlxContext, Screen
from src.screens import PlayGame, MainMenu, InstructionsScreen
from typing import Set
from src.Parser import Parser
from mlx import Mlx  # type: ignore[import-untyped]
import time


_KEY_PRESS_MASK = 1
_KEY_RELEASE_MASK = 2

_KEY_PRESS_EVENT = 2
_KEY_RELEASE_EVENT = 3

KEY_ESCAPE = 65307


class MainGameLoop:

    def __init__(self) -> None:
        self._config = Parser().parse("tests/jsons/valid_no_comments.json")
        self._state = GameState()
        self._mlx_ctx = self._init_mlx()
        self._main_menu_screen = MainMenu(self._mlx_ctx)
        self._instructions_screen = InstructionsScreen(self._mlx_ctx)
        self._game_screen = PlayGame(self._mlx_ctx, self._config)
        self._pressed_keys: Set[int] = set()

    def run(self) -> None:
        self._mlx_ctx.m.mlx_loop(self._mlx_ctx.mlx_ptr)

    def game_loop(self, param) -> int:
        now = time.time()
        delta_time = now - self._state.last_frame_time

        if delta_time < self._state.frame_interval:
            time.sleep(self._state.frame_interval - delta_time)
        now = time.time()
        delta_time = now - self._state.last_frame_time
        self._state.last_frame_time = time.time()
        delta_time = min(delta_time, 1 / 30)

        # update() & render() for all
        match self._state.screen:
            case Screen.MAIN_MENU:
                self._main_menu_screen.render()
            case Screen.GAME_PLAYING:
                self._game_screen.update(delta_time)
                self._game_screen.render()
            case Screen.INSTRUCTIONS:
                self._instructions_screen.render()
            case Screen.WIN_OR_LOSE:
                pass

        return 0

    def on_key(self, keycode: int, param) -> int:
        if keycode == KEY_ESCAPE:
            if self._state.screen == Screen.INSTRUCTIONS:
                self._state.screen = Screen.MAIN_MENU
            else:
                self._mlx_ctx.m.mlx_loop_exit(self._mlx_ctx.mlx_ptr)
            return 0

        if self._state.screen == Screen.MAIN_MENU:
            action = self._main_menu_screen.handle_key(keycode)
            if action is not None:
                self._activate_main_menu_action(action)
            return 0

        return 0

    def _activate_main_menu_action(self, action: str) -> None:
        if action == "start":
            self._state.screen = Screen.GAME_PLAYING
        elif action == "exit":
            self._mlx_ctx.m.mlx_loop_exit(self._mlx_ctx.mlx_ptr)
        elif action == "instructions":
            self._state.screen = Screen.INSTRUCTIONS
        elif action == "settings":
            print(" not active yet")
        elif action == "highscores":
            print(" not active yet")

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
        m.mlx_key_hook(win_ptr, self.on_key, None)

        return mlx_ctx
