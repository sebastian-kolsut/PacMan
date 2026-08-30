from typing import Tuple

from src.models import Direction
from src.models.dataclasses import MlxContext
from src.screens.game.ghosts.Ghost import Ghost
from src.screens.game.Maze import Maze


class Pinky(Ghost):
    """Ghost that tries to ambush Pac-Man."""

    def __init__(
        self,
        cell_size: int,
        mlx_ctx: MlxContext,
        maze: Maze,
        start_cell: Tuple[int, int],
    ) -> None:
        """Spawn Pinky at start_cell with her fixed speed and sprite.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the sprite buffer.
            maze: Maze Pinky moves through.
            start_cell: (x, y) cell to spawn in and respawn to.
        """
        super().__init__(
            cell_size,
            mlx_ctx,
            maze,
            "pinky",
            start_cell,
            speed_multiplier=2.8,
        )

    def _should_recalculate_direction(self) -> bool:
        """Always re-evaluate direction, so Pinky keeps ambushing."""
        return True

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        """Return the direction toward a cell ahead of Pac-Man.

        Falls back to targeting Pac-Man's exact cell if the ambush cell
        is unreachable.

        Args:
            pacman_cell: Pac-Man's current (x, y) cell.
            pacman_direction: Pac-Man's current facing direction.

        Returns:
            The direction toward the ambush target.
        """
        target_cell = self._get_ambush_target(
            pacman_cell,
            pacman_direction,
        )

        if not self._pathfinder.find_path(
            self._get_current_cell(),
            target_cell,
        ):
            target_cell = pacman_cell

        return self._choose_bfs_direction(target_cell)

    def _get_ambush_target(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Tuple[int, int]:
        """Return the cell three tiles ahead of Pac-Man's facing direction.

        Args:
            pacman_cell: Pac-Man's current (x, y) cell.
            pacman_direction: Direction Pac-Man is currently facing.

        Returns:
            The (x, y) cell 3 tiles ahead of Pac-Man in his facing
            direction, clamped to the maze bounds.
        """
        target_x, target_y = pacman_cell
        distance = 3

        if pacman_direction == Direction.UP:
            target_y -= distance
        elif pacman_direction == Direction.RIGHT:
            target_x += distance
        elif pacman_direction == Direction.DOWN:
            target_y += distance
        elif pacman_direction == Direction.LEFT:
            target_x -= distance

        target_x = max(0, min(target_x, self._maze.width - 1))
        target_y = max(0, min(target_y, self._maze.height - 1))

        return target_x, target_y
