from src.models.dataclasses import ProgramState, MlxContext, Screen, GameState
from src.Highscores import Highscores
from src.MusicPlayer import MusicPlayer
from src.screens import PlayGame, MainMenu, InstructionsScreen, \
    WinLoseScreen, HighscoresScreen, SettingsScreen
from typing import Set
from numpy.typing import NDArray
import numpy as np
from src.Parser import Parser
from mlx import Mlx  # type: ignore[import-untyped]
import time


_KEY_PRESS_MASK = 1
_KEY_RELEASE_MASK = 2

_KEY_PRESS_EVENT = 2
_KEY_RELEASE_EVENT = 3

KEY_ESCAPE = 65307
KEY_ENTER = 65293


class MainGameLoop:

    def __init__(self) -> None:
        self._config = Parser().parse("config.json")
        self._state = ProgramState()
        self._music = MusicPlayer(self._state)
        self._mlx_ctx = self._init_mlx()
        self._scores = Highscores(self._config.highscore_filename)
        self._main_menu_screen = MainMenu(self._mlx_ctx, self._scores)
        self._instructions_screen = InstructionsScreen(self._mlx_ctx)
        self._highscores = HighscoresScreen(self._scores, self._mlx_ctx)
        self._win_lose_screen = WinLoseScreen(self._mlx_ctx, self._state)
        self._game_screen = PlayGame(self._mlx_ctx, self._config, self._state)
        self._settings_screen = SettingsScreen(self._mlx_ctx, self._state)
        self._settings_return_screen = Screen.MAIN_MENU
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

        self._music.update()

        # update() & render() for all
        match self._state.screen:
            case Screen.MAIN_MENU:
                self._main_menu_screen.render()
            case Screen.GAME_PLAYING:
                self._game_screen.update(delta_time)
                self._game_screen.render()
            case Screen.INSTRUCTIONS:
                self._instructions_screen.render()
            case Screen.HIGHSCORES:
                self._highscores.render()
            case Screen.WIN_OR_LOSE:
                score = self._game_screen.get_final_score()
                self._win_lose_screen.update(
                    self._scores.is_score_eligible(score), self._scores, score
                    )
                self._win_lose_screen.render(self._game_screen.get_image())
            case Screen.SETTINGS:
                background, dim_background = self._get_settings_background()
                self._settings_screen.render(background, dim_background)

        return 0

    def _get_settings_background(self) -> tuple[NDArray[np.uint8], bool]:
        if self._settings_return_screen == Screen.GAME_PLAYING:
            # Already dimmed by PauseScreen - avoid dimming it twice.
            return self._game_screen.get_image(), False
        return self._main_menu_screen.get_image(), True

    def on_key(self, keycode: int, param) -> int:
        if self._state.screen == Screen.SETTINGS:
            action = self._settings_screen.handle_key(keycode)
            if action == "close":
                self._state.screen = self._settings_return_screen
            return 0

        if self._state.screen == Screen.WIN_OR_LOSE:
            action = self._win_lose_screen.handle_key(keycode)
            if action == "restart":
                self._restart_game()
            elif action == "main_menu":
                self._reset_game()
                self._state.screen = Screen.MAIN_MENU
            elif action is not None:
                self._activate_main_menu_action(action)
            return 0

        if keycode == KEY_ESCAPE and self._state.screen == Screen.MAIN_MENU:
            self._mlx_ctx.m.mlx_loop_exit(self._mlx_ctx.mlx_ptr)
            return 0

        if self._state.screen == Screen.INSTRUCTIONS:
            action = self._instructions_screen.handle_key(keycode)
            if action == "main_menu":
                self._state.screen = Screen.MAIN_MENU
            return 0

        if keycode == KEY_ESCAPE and self._state.screen == Screen.HIGHSCORES:
            self._state.screen = Screen.MAIN_MENU
            return 0

        if self._state.screen == Screen.MAIN_MENU:
            action = self._main_menu_screen.handle_key(keycode)
            if action is not None:
                self._activate_main_menu_action(action)
            return 0

        if self._state.screen == Screen.GAME_PLAYING:
            action = self._game_screen.handle_key(keycode)
            if action == "restart":
                self._restart_game()
            elif action == "settings":
                self._open_settings(Screen.GAME_PLAYING)
            return 0

        return 0

    def _open_settings(self, return_screen: Screen) -> None:
        self._settings_return_screen = return_screen
        self._state.screen = Screen.SETTINGS

    def _activate_main_menu_action(self, action: str) -> None:
        if action == "start":
            self._restart_game()
        elif action == "exit":
            self._mlx_ctx.m.mlx_loop_exit(self._mlx_ctx.mlx_ptr)
        elif action == "instructions":
            self._instructions_screen.reset()
            self._state.screen = Screen.INSTRUCTIONS
        elif action == "settings":
            self._open_settings(Screen.MAIN_MENU)
        elif action == "highscores":
            self._state.screen = Screen.HIGHSCORES

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

    def _reset_game(self) -> None:
        self._game_screen = PlayGame(
            self._mlx_ctx,
            self._config,
            self._state,
        )

    def _restart_game(self) -> None:
        self._reset_game()
        self._state.state = GameState.PLAYING
        self._state.screen = Screen.GAME_PLAYING
