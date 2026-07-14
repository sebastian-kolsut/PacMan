from collections import deque
from random import choice, shuffle
from typing import Dict, List, Tuple

from numpy.typing import NDArray

from src.models import Direction
from src.models.dataclasses import MlxContext
from src.screens.game.Character import Character
from src.screens.game.Maze import Maze


_GHOST_ASSETS = {
    "blinky": "assets/ghosts/blinky.png",
    "clyde": "assets/ghosts/clyde.png",
}

_DIRECTIONS = [
    Direction.UP,
    Direction.RIGHT,
    Direction.DOWN,
    Direction.LEFT,
]


class Ghost(Character):

    def __init__(
        self,
        cell_size: int,
        mlx_ctx: MlxContext,
        maze: Maze,
        asset_name: str,
        start_cell: Tuple[int, int],
        behavior: str,
    ) -> None:
        super().__init__(cell_size, mlx_ctx, maze)

        self._behavior = behavior
        self._asset = self._fb.get_image_array(
            _GHOST_ASSETS[asset_name],
            self._character_size,
            self._character_size,
        )

        start_x, start_y = self._find_valid_spawn(start_cell)
        self._pos_x = float(start_x * self._cell_size)
        self._pos_y = float(start_y * self._cell_size)

        self._speed = self._cell_size * 2.0
        self._direction = self._get_random_valid_direction()
        self._pending_direction = self._direction

    def update(self, delta_time: float, pacman_cell: Tuple[int, int]) -> None:
        if self._is_close_to_cell_center():
            self._snap_to_cell()  # round cell

            valid_directions = self._get_valid_directions()
            if not valid_directions:
                return

            if self._behavior == "chase":
                self._pending_direction = self._choose_direction(pacman_cell)
            elif self._direction not in valid_directions or choice(
                                                            [0, 1, 2]) == 0:
                self._pending_direction = self._choose_direction(pacman_cell)

        self._try_turn(delta_time)

        next_x, next_y = self._get_next_step_xy(delta_time)

        if self._check_for_wall(next_x, next_y, self._direction):
            self._snap_to_cell()
            valid_directions = self._get_valid_directions()
            if valid_directions:
                self._direction = self._choose_direction(pacman_cell)
                self._pending_direction = self._direction
            return

        self._pos_x = next_x
        self._pos_y = next_y

    def render(self) -> NDArray:
        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]

        self._fb.draw_blended_tile(
            pixels,
            self._asset,
            0,
            0,
        )

        return pixels

    def get_draw_position(self) -> Tuple[int, int]:
        return (
            int(self._pos_y) + self._offset,
            int(self._pos_x) + self._offset,
        )

    def _choose_direction(self, pacman_cell: Tuple[int, int]) -> Direction:
        valid_directions = self._get_valid_directions()

        if not valid_directions:
            return self._direction

        if self._behavior == "chase":
            return self._choose_bfs_direction(pacman_cell)

        return choice(self._get_valid_directions_without_reverse())

    def _choose_bfs_direction(self, target_cell: Tuple[int, int]) -> Direction:
        start_cell = self._get_current_cell()
        path = self._find_path(start_cell, target_cell)

        if len(path) < 2:
            valid_directions = self._get_valid_directions()
            if self._direction in valid_directions:
                return self._direction
            if valid_directions:
                return choice(valid_directions)
            return self._direction

        next_cell = path[1]
        return self._direction_to_cell(start_cell, next_cell)

    def _find_path(
        self,
        start_cell: Tuple[int, int],
        target_cell: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        queue = deque([start_cell])
        came_from: Dict[Tuple[int, int], Tuple[int, int] | None] = {
            start_cell: None,
        }

        while queue:
            current_cell = queue.popleft()

            if current_cell == target_cell:
                break

            for next_cell in self._get_neighbor_cells(current_cell):
                if next_cell not in came_from:
                    came_from[next_cell] = current_cell
                    queue.append(next_cell)

        if target_cell not in came_from:
            return []

        path = []
        current: Tuple[int, int] | None = target_cell

        while current is not None:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def _get_neighbor_cells(
        self,
        cell: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        cell_x, cell_y = cell
        neighbors = []

        for direction in _DIRECTIONS:
            if self._can_move_from_cell(cell_x, cell_y, direction):
                neighbors.append(
                    self._get_next_cell_from_direction(
                        cell_x,
                        cell_y,
                        direction,
                    )
                )

        return neighbors

    def _is_close_to_cell_center(self) -> bool:
        tolerance = max(2.0, self._speed / 60.0)

        x_remainder = self._pos_x % self._cell_size
        y_remainder = self._pos_y % self._cell_size

        return (
            x_remainder <= tolerance
            or self._cell_size - x_remainder <= tolerance
        ) and (
            y_remainder <= tolerance
            or self._cell_size - y_remainder <= tolerance
        )

    def _snap_to_cell(self) -> None:
        self._pos_x = float(
            round(self._pos_x / self._cell_size) * self._cell_size
        )
        self._pos_y = float(
            round(self._pos_y / self._cell_size) * self._cell_size
        )

    def _get_current_cell(self) -> Tuple[int, int]:
        cell_x = int(round(self._pos_x / self._cell_size))
        cell_y = int(round(self._pos_y / self._cell_size))

        cell_x = max(0, min(cell_x, self._maze.width - 1))
        cell_y = max(0, min(cell_y, self._maze.height - 1))

        return cell_x, cell_y

    def _get_valid_directions(self) -> List[Direction]:
        cell_x, cell_y = self._get_current_cell()
        valid_directions = []

        for direction in _DIRECTIONS:
            if self._can_move_from_cell(cell_x, cell_y, direction):
                valid_directions.append(direction)

        return valid_directions

    def _can_move_from_cell(
        self,
        cell_x: int,
        cell_y: int,
        direction: Direction,
    ) -> bool:
        next_x, next_y = self._get_next_cell_from_direction(
            cell_x,
            cell_y,
            direction,
        )

        if (
            next_x < 0
            or next_x >= self._maze.width
            or next_y < 0
            or next_y >= self._maze.height
        ):
            return False

        cell_idx = cell_y * self._maze.width + cell_x
        return not self._maze.is_wall_direction(cell_idx, direction)

    def _get_next_cell_from_direction(
        self,
        cell_x: int,
        cell_y: int,
        direction: Direction,
    ) -> Tuple[int, int]:
        if direction == Direction.UP:
            return cell_x, cell_y - 1
        if direction == Direction.RIGHT:
            return cell_x + 1, cell_y
        if direction == Direction.DOWN:
            return cell_x, cell_y + 1
        if direction == Direction.LEFT:
            return cell_x - 1, cell_y

        return cell_x, cell_y

    def _direction_to_cell(
        self,
        current_cell: Tuple[int, int],
        next_cell: Tuple[int, int],
    ) -> Direction:
        current_x, current_y = current_cell
        next_x, next_y = next_cell

        if next_y < current_y:
            return Direction.UP
        if next_x > current_x:
            return Direction.RIGHT
        if next_y > current_y:
            return Direction.DOWN
        if next_x < current_x:
            return Direction.LEFT

        return self._direction

    def _get_random_valid_direction(self) -> Direction:
        valid_directions = self._get_valid_directions()
        if valid_directions:
            return choice(valid_directions)
        return Direction.RIGHT

    def _find_valid_spawn(
            self, start_cell: Tuple[int, int]) -> Tuple[int, int]:
        start_x, start_y = start_cell

        candidates = [
            (start_x, start_y),
            (start_x + 1, start_y),
            (start_x, start_y + 1),
            (start_x - 1, start_y),
            (start_x, start_y - 1),
            (start_x + 1, start_y + 1),
            (start_x - 1, start_y + 1),
            (start_x + 1, start_y - 1),
            (start_x - 1, start_y - 1),
        ]

        shuffle(candidates)

        for cell_x, cell_y in candidates:
            if (
                0 <= cell_x < self._maze.width
                and 0 <= cell_y < self._maze.height
                and self._cell_has_exit(cell_x, cell_y)
            ):
                return cell_x, cell_y

        return max(0, min(start_x, self._maze.width - 1)), max(
            0,
            min(start_y, self._maze.height - 1),
        )

    def _cell_has_exit(self, cell_x: int, cell_y: int) -> bool:
        return any(
            self._can_move_from_cell(cell_x, cell_y, direction)
            for direction in _DIRECTIONS
        )

    def _get_opposite_direction(self, direction: Direction) -> Direction:
        if direction == Direction.UP:
            return Direction.DOWN
        if direction == Direction.DOWN:
            return Direction.UP
        if direction == Direction.LEFT:
            return Direction.RIGHT
        if direction == Direction.RIGHT:
            return Direction.LEFT

        return direction

    def _get_valid_directions_without_reverse(self) -> List[Direction]:
        valid_directions = self._get_valid_directions()

        if len(valid_directions) <= 1:
            return valid_directions

        opposite = self._get_opposite_direction(self._direction)

        filtered = [
            direction
            for direction in valid_directions
            if direction != opposite
        ]

        if filtered:
            return filtered

        return valid_directions
