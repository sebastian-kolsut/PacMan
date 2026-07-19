from random import choice
from typing import Optional, Tuple

from src.models import Direction
from src.models.dataclasses import MlxContext
from src.screens.game.ghosts.Ghost import Ghost
from src.screens.game.Maze import Maze


class Inky(Ghost):
    """Ghost that sometimes chases and sometimes roams."""

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
            "inky",
            start_cell,
            speed_multiplier=1.9,
        )
        self._target_cell: Optional[Tuple[int, int]] = None
        self._mode = "roam"
        self._steps_left = 0

    def _should_recalculate_direction(self) -> bool:
        return True

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        if self._steps_left <= 0:
            self._mode = choice(["chase", "roam"])
            self._steps_left = choice([4, 5, 6, 7])

            if self._mode == "roam":
                self._target_cell = self._get_random_reachable_cell()

        self._steps_left -= 1

        if self._mode == "chase":
            return self._choose_bfs_direction(pacman_cell)

        current_cell = self._get_current_cell()

        if self._target_cell is None or current_cell == self._target_cell:
            self._target_cell = self._get_random_reachable_cell()

        return self._choose_bfs_direction(self._target_cell)