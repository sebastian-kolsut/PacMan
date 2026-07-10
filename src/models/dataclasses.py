from enum import Enum, auto
from dataclasses import dataclass, field
from mlx import Mlx  # type: ignore[import-untyped]
import time


class Screen(Enum):

    MAIN_MENU = auto()
    GAME_PLAYING = auto()
    INSTRUCTIONS = auto()
    WIN_OR_LOSE = auto()


class Direction(int, Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


@dataclass
class GameState:

    screen: Screen = Screen.MAIN_MENU
    last_frame_time: float = field(default_factory=time.time)
    frame_interval: float = 1 / 60


@dataclass
class MlxContext:

    m: Mlx
    mlx_ptr: int
    win_ptr: int

    win_width: int
    win_height: int
