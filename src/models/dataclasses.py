from enum import Enum, auto
from dataclasses import dataclass, field
from mlx import Mlx
import time


class Screen(Enum):
    """Every top-level screen the game can display."""

    MAIN_MENU = auto()
    GAME_PLAYING = auto()
    INSTRUCTIONS = auto()
    HIGHSCORES = auto()
    WIN_OR_LOSE = auto()
    SETTINGS = auto()


class Direction(int, Enum):
    """A cardinal movement direction, also usable as a wall-bit index."""

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class GameState(Enum):
    """The outcome of the current game run."""

    LOST = auto()
    WON = auto()
    PLAYING = auto()


@dataclass
class ProgramState:
    """Shared mutable state read and written across all screens.

    Attributes:
        screen: The screen currently being shown.
        last_frame_time: Timestamp of the previous frame, for delta timing.
        state: Whether the game is currently playing, won or lost.
        frame_interval: Minimum seconds between frames (frame rate cap).
        wall_theme_index: Index into WALL_THEMES for the active maze color.
        level: 0-based index of the current level.
        music_volume: Music volume, from 0 to 10.
    """

    screen: Screen = Screen.MAIN_MENU
    last_frame_time: float = field(default_factory=time.time)
    state: GameState = GameState.PLAYING
    frame_interval: float = 1 / 120
    wall_theme_index: int = 0
    level: int = 0
    music_volume: int = 5


@dataclass
class MlxContext:
    """The MLX handles and window dimensions shared across all renderers.

    Attributes:
        m: The MLX binding instance.
        mlx_ptr: Pointer to the MLX display context.
        win_ptr: Pointer to the game window.
        win_width: Window width in pixels.
        win_height: Window height in pixels.
    """

    m: Mlx
    mlx_ptr: int
    win_ptr: int

    win_width: int
    win_height: int
