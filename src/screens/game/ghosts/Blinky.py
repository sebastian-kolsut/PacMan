from typing import Tuple

from src.models import Direction
from src.models.dataclasses import MlxContext
from src.screens.game.ghosts.Ghost import Ghost
from src.screens.game.Maze import Maze


class Blinky(Ghost):
    """Blinky chases Pac-Man directly."""

    def __init__(
        self,
        cell_size: int,
        mlx_ctx: MlxContext,
        maze: Maze,
        start_cell: Tuple[int, int],
    ) -> None:
        super().__init__(
            cell_size,
            mlx_ctx,
            maze,
            "blinky",
            start_cell,
            speed_multiplier=2.2,
        )

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        return self._choose_bfs_direction(pacman_cell)

    def _should_recalculate_direction(self) -> bool:
        return True
