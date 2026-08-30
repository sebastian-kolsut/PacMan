from collections import deque
from typing import Dict, List, Tuple

from src.models import Direction
from src.screens.game.Maze import Maze


_DIRECTIONS = (
    Direction.UP,
    Direction.RIGHT,
    Direction.DOWN,
    Direction.LEFT,
)


class Pathfinder:
    """Breadth-first search helper for navigating the maze grid."""

    def __init__(self, maze: Maze) -> None:
        """Initialize the pathfinder for the given maze.

        Args:
            maze: Maze whose wall bitboards define which cells connect.
        """
        self._maze = maze

    def find_path(
        self,
        start_cell: Tuple[int, int],
        target_cell: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Find the shortest path between two cells via breadth-first search.

        Args:
            start_cell: (x, y) cell to start from.
            target_cell: (x, y) cell to reach.

        Returns:
            The list of cells from start to target inclusive, or an empty
            list if target_cell is unreachable from start_cell.
        """
        queue = deque([start_cell])
        came_from: Dict[Tuple[int, int], Tuple[int, int] | None] = {
            start_cell: None,
        }

        while queue:
            current_cell = queue.popleft()

            if current_cell == target_cell:
                break

            for next_cell in self.get_neighbor_cells(current_cell):
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

    def next_direction(
        self,
        start_cell: Tuple[int, int],
        target_cell: Tuple[int, int],
    ) -> Direction | None:
        """Return the first step direction of the shortest path to a cell.

        Args:
            start_cell: (x, y) cell to start from.
            target_cell: (x, y) cell to reach.

        Returns:
            The direction to move from start_cell, or None if no path
            exists (target unreachable, or start equals target).
        """
        path = self.find_path(start_cell, target_cell)

        if len(path) < 2:
            return None

        return self.direction_to_cell(path[0], path[1])

    def get_neighbor_cells(
        self,
        cell: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Return the cells directly reachable from cell (no walls between).

        Args:
            cell: (x, y) cell to look around.

        Returns:
            The list of adjacent cells with no wall blocking the way.
        """
        return [
            self.get_next_cell(cell, direction)
            for direction in self.get_valid_directions(cell)
        ]

    def get_valid_directions(self, cell: Tuple[int, int]) -> List[Direction]:
        """Return the directions in which cell has no blocking wall.

        Args:
            cell: (x, y) cell to check.

        Returns:
            The list of directions that are not blocked by a wall.
        """
        cell_x, cell_y = cell
        return [
            direction
            for direction in _DIRECTIONS
            if self._can_move_from_cell(cell_x, cell_y, direction)
        ]

    def get_reachable_cells(
        self,
        start_cell: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Return every cell reachable from start_cell via open corridors.

        Args:
            start_cell: (x, y) cell to start the search from.

        Returns:
            The list of cells reachable from start_cell, start_cell
            included.
        """
        queue = deque([start_cell])
        visited = {start_cell}

        while queue:
            current_cell = queue.popleft()

            for next_cell in self.get_neighbor_cells(current_cell):
                if next_cell not in visited:
                    visited.add(next_cell)
                    queue.append(next_cell)

        return list(visited)

    def get_next_cell(
        self,
        cell: Tuple[int, int],
        direction: Direction,
    ) -> Tuple[int, int]:
        """Return the cell one step away from cell in the given direction.

        Args:
            cell: (x, y) starting cell.
            direction: Direction to step in.

        Returns:
            The (x, y) cell one step from cell in direction. Returns cell
            unchanged if direction is not one of the four cardinal
            directions.
        """
        cell_x, cell_y = cell

        if direction == Direction.UP:
            return cell_x, cell_y - 1
        if direction == Direction.RIGHT:
            return cell_x + 1, cell_y
        if direction == Direction.DOWN:
            return cell_x, cell_y + 1
        if direction == Direction.LEFT:
            return cell_x - 1, cell_y

        return cell

    def direction_to_cell(
        self,
        current_cell: Tuple[int, int],
        next_cell: Tuple[int, int],
    ) -> Direction:
        """Return the direction that moves from current_cell to next_cell.

        Args:
            current_cell: (x, y) starting cell.
            next_cell: (x, y) cell adjacent to current_cell.

        Returns:
            The direction of travel from current_cell to next_cell.

        Raises:
            ValueError: If the two cells are not adjacent.
        """
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

        raise ValueError("Cells must be adjacent to determine direction")

    def _can_move_from_cell(
        self,
        cell_x: int,
        cell_y: int,
        direction: Direction,
    ) -> bool:
        """Return whether cell_x, cell_y has an open path in direction.

        Args:
            cell_x: X coordinate of the cell to check.
            cell_y: Y coordinate of the cell to check.
            direction: Direction to check for an open path.

        Returns:
            True if the neighbor cell exists within the maze bounds and no
            wall blocks the move, False otherwise.
        """
        next_x, next_y = self.get_next_cell((cell_x, cell_y), direction)

        if (
            next_x < 0
            or next_x >= self._maze.width
            or next_y < 0
            or next_y >= self._maze.height
        ):
            return False

        cell_idx = cell_y * self._maze.width + cell_x
        return not self._maze.is_wall_direction(cell_idx, direction)
