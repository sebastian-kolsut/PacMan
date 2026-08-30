from types import SimpleNamespace
from typing import Callable, cast

import numpy as np
import pytest

from src.models import Direction
from src.screens.game.Pathfinder import Pathfinder
from src.screens.game.ghosts import Blinky, Ghost, Pinky


class _OpenMaze:

    def __init__(self, width: int = 7, height: int = 7) -> None:
        self.width = width
        self.height = height

    def is_wall_direction(self, cell_idx: int, direction: Direction) -> bool:
        return False


class _MazeWithBlockedExit(_OpenMaze):
    def __init__(self, blocked_cell: tuple[int, int],
                 blocked_direction: Direction) -> None:
        super().__init__()
        self._blocked_cell = blocked_cell
        self._blocked_direction = blocked_direction

    def is_wall_direction(self, cell_idx: int, direction: Direction) -> bool:
        cell = (cell_idx % self.width, cell_idx // self.width)
        return (
            cell == self._blocked_cell
            and direction == self._blocked_direction
        )


class _FrameBuffer:

    def __init__(self, mlx_ctx: object, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.img_ptr = 0

    def get_image_array(
        self,
        path: str,
        width: int,
        height: int,
    ) -> np.ndarray:
        return np.full((height, width, 4), 255, dtype=np.uint8)

    def get_array(self) -> np.ndarray:
        return np.zeros((self.height, self.width, 4), dtype=np.uint8)

    def draw_blended_tile(
        self,
        pixels: np.ndarray,
        asset: np.ndarray,
        x: int,
        y: int,
    ) -> None:
        pixels[:, :] = asset


@pytest.fixture(autouse=True)
def replace_framebuffer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.screens.game.Character.FrameBuffer",
        _FrameBuffer,
    )


def _make_ghost(ghost_class: Callable[..., Ghost],
                start_cell: tuple[int, int] = (3, 3)) -> Ghost:
    return ghost_class(
        cell_size=10,
        mlx_ctx=SimpleNamespace(),
        maze=_OpenMaze(),
        start_cell=start_cell,
    )


def test_blinky_chooses_shortest_direction_toward_pacman() -> None:
    blinky = _make_ghost(Blinky)

    direction = blinky._choose_direction((5, 3), Direction.RIGHT)

    assert direction == Direction.RIGHT


def test_blinky_chooses_a_detour_when_direct_path_is_blocked() -> None:
    blinky = Blinky(
        cell_size=10,
        mlx_ctx=SimpleNamespace(),  # type: ignore[arg-type]
        maze=_MazeWithBlockedExit(  # type: ignore[arg-type]
            (3, 3), Direction.RIGHT),
        start_cell=(3, 3),
    )

    direction = blinky._choose_direction((5, 3), Direction.RIGHT)

    assert direction == Direction.UP


def test_pathfinder_returns_a_detour_around_a_blocked_exit() -> None:
    pathfinder = Pathfinder(
        _MazeWithBlockedExit(  # type: ignore[arg-type]
            (3, 3), Direction.RIGHT),
    )

    path = pathfinder.find_path((3, 3), (5, 3))

    assert path[0] == (3, 3)
    assert path[1] == (3, 2)
    assert path[-1] == (5, 3)


def test_pinky_targets_three_cells_ahead_of_pacman() -> None:
    pinky = cast(Pinky, _make_ghost(Pinky))

    target_cell = pinky._get_ambush_target((2, 3), Direction.RIGHT)

    assert target_cell == (5, 3)


def test_pinky_chooses_a_direction_using_pathfinder() -> None:
    pinky = _make_ghost(Pinky)

    direction = pinky._choose_direction((5, 3), Direction.RIGHT)

    assert direction == Direction.RIGHT


def test_frightened_ghost_slows_down_and_moves_away_from_pacman() -> None:
    blinky = _make_ghost(Blinky)

    blinky.set_frightened(True)

    assert blinky.get_speed_multiplier() == pytest.approx(1.3)
    assert blinky._choose_flee_direction((0, 0)) == Direction.RIGHT


def test_eaten_ghost_is_invisible_then_respawns_after_five_seconds() -> None:
    blinky = _make_ghost(Blinky)
    start_position = blinky.get_draw_position()

    blinky.eat()

    assert blinky.is_eaten()
    assert not blinky.render().any()

    blinky.update(4.9, (6, 6), Direction.RIGHT)
    assert blinky.is_eaten()

    blinky.update(0.1, (6, 6), Direction.RIGHT)

    assert not blinky.is_eaten()
    assert blinky.get_draw_position() == start_position
    assert blinky.get_speed_multiplier() == pytest.approx(3.0)
