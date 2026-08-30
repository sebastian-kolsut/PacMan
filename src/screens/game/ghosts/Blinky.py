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
        """Spawn Blinky at start_cell with his fixed speed and sprite.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the sprite buffer.
            maze: Maze Blinky moves through.
            start_cell: (x, y) cell to spawn in and respawn to.
        """
        super().__init__(
            cell_size,
            mlx_ctx,
            maze,
            "blinky",
            start_cell,
            speed_multiplier=3.0,
        )

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        """Return the direction of the shortest path straight to Pac-Man.

        Args:
            pacman_cell: Pac-Man's current (x, y) cell.
            pacman_direction: Pac-Man's current facing direction (unused;
                Blinky always targets Pac-Man's exact cell).

        Returns:
            The direction toward pacman_cell.
        """
        return self._choose_bfs_direction(pacman_cell)

    def _should_recalculate_direction(self) -> bool:
        """Always re-evaluate direction, so Blinky keeps closing in."""
        return True
