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
        """Spawn Inky at start_cell with his fixed speed and sprite.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the sprite buffer.
            maze: Maze Inky moves through.
            start_cell: (x, y) cell to spawn in and respawn to.
        """
        super().__init__(
            cell_size,
            mlx_ctx,
            maze,
            "inky",
            start_cell,
            speed_multiplier=2.5,
        )
        self._target_cell: Optional[Tuple[int, int]] = None
        self._mode = "roam"
        self._steps_left = 0

    def _should_recalculate_direction(self) -> bool:
        """Always re-evaluate direction, so Inky can switch mode mid-path."""
        return True

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        """Return the direction to move, alternating chase and roam modes.

        Picks a new random mode and duration whenever the current one
        runs out, chasing Pac-Man directly in "chase" mode or heading to
        a random reachable cell in "roam" mode.

        Args:
            pacman_cell: Pac-Man's current (x, y) cell.
            pacman_direction: Pac-Man's current facing direction (unused).

        Returns:
            The direction toward the current chase or roam target.
        """
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
