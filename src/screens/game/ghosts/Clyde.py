from typing import Optional, Tuple

from src.models import Direction
from src.models.dataclasses import MlxContext
from src.screens.game.ghosts.Ghost import Ghost
from src.screens.game.Maze import Maze


class Clyde(Ghost):
    """Ghost that walks to random reachable cells."""

    def __init__(
        self,
        cell_size: int,
        mlx_ctx: MlxContext,
        maze: Maze,
        start_cell: Tuple[int, int],
    ) -> None:
        """Spawn Clyde at start_cell with his fixed speed and sprite.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the sprite buffer.
            maze: Maze Clyde moves through.
            start_cell: (x, y) cell to spawn in and respawn to.
        """
        super().__init__(
            cell_size,
            mlx_ctx,
            maze,
            "clyde",
            start_cell,
            speed_multiplier=2.9,
        )
        self._target_cell: Optional[Tuple[int, int]] = None

    def _should_recalculate_direction(self) -> bool:
        """Always re-evaluate direction, so Clyde keeps wandering."""
        return True

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        """Return the direction toward a random reachable roaming target.

        Picks a new random target cell whenever the previous one is
        reached (or none has been picked yet).

        Args:
            pacman_cell: Pac-Man's current (x, y) cell (unused; Clyde
                ignores Pac-Man entirely).
            pacman_direction: Pac-Man's current facing direction (unused).

        Returns:
            The direction toward Clyde's current roaming target.
        """
        current_cell = self._get_current_cell()

        if self._target_cell is None or current_cell == self._target_cell:
            self._target_cell = self._get_random_reachable_cell()

        return self._choose_bfs_direction(self._target_cell)
