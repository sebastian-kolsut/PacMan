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
        super().__init__(
            cell_size,
            mlx_ctx,
            maze,
            "pinky",
            start_cell,
            speed_multiplier=2.0,
        )

    def _should_recalculate_direction(self) -> bool:
        return True

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        target_cell = self._get_ambush_target(
            pacman_cell,
            pacman_direction,
        )

        if not self._find_path(self._get_current_cell(), target_cell):
            target_cell = pacman_cell

        return self._choose_bfs_direction(target_cell)

    def _get_ambush_target(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Tuple[int, int]:
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