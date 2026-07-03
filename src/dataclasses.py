from enum import Enum, auto
from dataclasses import dataclass, field
from mlx import Mlx  # type: ignore[import-untyped]
import time


class Screen(Enum):

    MAIN_MENU = auto()
    GAME_PLAYING = auto()
    WIN_OR_LOSE = auto()


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


@dataclass
class MazeBitmaps:

    maze_width: int
    maze_height: int

    north_walls: int
    east_walls: int
    south_walls: int
    west_walls: int
