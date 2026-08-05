from random import choice
from typing import List, Tuple

from numpy.typing import NDArray

from src.models import Direction
from src.models.dataclasses import MlxContext
from src.screens.game.Character import Character
from src.screens.game.Maze import Maze
from src.screens.game.Pathfinder import Pathfinder
from src.screens.game.ghosts.GhostState import GhostState


_GHOST_ASSETS = {
    "blinky": "assets/ghosts/blinky2.png",
    "clyde": "assets/ghosts/clyde.png",
    "pinky": "assets/ghosts/pinky.png",
    "inky": "assets/ghosts/inky.png",
}

_BLUE_GHOST_ASSET = "assets/ghosts/blue_ghost.png"

_DEFAULT_SPEED_MULTIPLIER = 2.0
_MIN_SPEED_MULTIPLIER = 1.8
_MAX_SPEED_MULTIPLIER = 5.0
_FRIGHTENED_SPEED_MULTIPLIER = 1.8


class Ghost(Character):

    def __init__(
        self,
        cell_size: int,
        mlx_ctx: MlxContext,
        maze: Maze,
        asset_name: str,
        start_cell: Tuple[int, int],
        speed_multiplier: float = _DEFAULT_SPEED_MULTIPLIER,
    ) -> None:
        super().__init__(cell_size, mlx_ctx, maze)
        self._pathfinder = Pathfinder(maze)

        self._asset = self._fb.get_image_array(
            _GHOST_ASSETS[asset_name],
            self._character_size,
            self._character_size,
        )

        self._normal_asset = self._asset
        self._blue_asset = self._fb.get_image_array(
            _BLUE_GHOST_ASSET,
            self._character_size,
            self._character_size,
        )
        self._state = GhostState()
        self._normal_speed_multiplier = speed_multiplier

        start_x, start_y = start_cell
        start_x = max(0, min(start_x, self._maze.width - 1))
        start_y = max(0, min(start_y, self._maze.height - 1))

        self._pos_x = float(start_x * self._cell_size)
        self._pos_y = float(start_y * self._cell_size)

        self.set_speed_multiplier(speed_multiplier)
        self._direction = self._get_random_valid_direction()
        self._pending_direction = self._direction
        self._save_start_state()

    def update(
        self,
        delta_time: float,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> None:
        if self._state.is_eaten:
            if self._state.update(delta_time):
                self.set_speed_multiplier(self._normal_speed_multiplier)
                self.reset_position()
            return

        self._state.update(delta_time)

        if self._is_close_to_cell_center(delta_time):
            self._snap_to_cell()  # round cell

            valid_directions = self._get_valid_directions()
            if not valid_directions:
                return

            if (
                self._should_recalculate_direction()
                or self._direction not in valid_directions
            ):
                if self._state.is_frightened:
                    self._pending_direction = self._choose_flee_direction(
                        pacman_cell)
                else:
                    self._pending_direction = self._choose_direction(
                        pacman_cell,
                        pacman_direction,
                    )

        self._try_turn(delta_time)

        next_x, next_y = self._get_next_step_xy(delta_time)

        if self._check_for_wall(next_x, next_y, self._direction):
            self._snap_to_cell()
            valid_directions = self._get_valid_directions()
            if valid_directions:
                if self._state.is_frightened:
                    self._direction = self._choose_flee_direction(pacman_cell)
                else:
                    self._direction = self._choose_direction(
                        pacman_cell,
                        pacman_direction,
                    )
                self._pending_direction = self._direction
            return

        self._pos_x = next_x
        self._pos_y = next_y

    def _should_recalculate_direction(self) -> bool:
        return False

    def render(self) -> NDArray:
        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]

        if self._state.is_eaten:
            return pixels

        if self._state.is_frightened:
            asset = self._blue_asset if self._state.show_blue_asset else \
                self._normal_asset
        else:
            asset = self._normal_asset

        self._fb.draw_blended_tile(
            pixels,
            asset,
            0,
            0,
        )

        return pixels

    def get_draw_position(self) -> Tuple[int, int]:
        return (
            int(self._pos_y) + self._offset,
            int(self._pos_x) + self._offset,
        )

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        valid_directions = self._get_valid_directions()

        if valid_directions:
            return choice(valid_directions)

        return self._direction

    def _choose_bfs_direction(self, target_cell: Tuple[int, int]) -> Direction:
        start_cell = self._get_current_cell()
        direction = self._pathfinder.next_direction(start_cell, target_cell)

        if direction is None:
            valid_directions = self._get_valid_directions()
            if self._direction in valid_directions:
                return self._direction
            if valid_directions:
                return choice(valid_directions)
            return self._direction

        return direction

    def _get_valid_directions(self) -> List[Direction]:
        return self._pathfinder.get_valid_directions(
            self._get_current_cell(),
        )

    def _get_random_valid_direction(self) -> Direction:
        valid_directions = self._get_valid_directions()
        if valid_directions:
            return choice(valid_directions)
        return Direction.RIGHT

    def set_speed_multiplier(self, speed_multiplier: float) -> None:
        speed_multiplier = max(
            _MIN_SPEED_MULTIPLIER,
            min(speed_multiplier, _MAX_SPEED_MULTIPLIER),
        )
        self._speed = self._cell_size * speed_multiplier

    def get_speed_multiplier(self) -> float:
        return self._speed / self._cell_size

    def _get_random_reachable_cell(self) -> Tuple[int, int]:
        current_cell = self._get_current_cell()
        reachable_cells = self._pathfinder.get_reachable_cells(current_cell)

        if len(reachable_cells) <= 1:
            return current_cell

        reachable_cells = [
            cell
            for cell in reachable_cells
            if cell != current_cell
        ]

        return choice(reachable_cells)

    def set_frightened(self, is_frightened: bool) -> None:
        if self._state.is_eaten:
            return

        self._state.set_frightened(is_frightened)

        if is_frightened:
            self.set_speed_multiplier(_FRIGHTENED_SPEED_MULTIPLIER)
        else:
            self.set_speed_multiplier(self._normal_speed_multiplier)

    def is_frightened(self) -> bool:
        return self._state.is_frightened

    def _choose_flee_direction(
        self,
        pacman_cell: Tuple[int, int],
    ) -> Direction:
        valid_directions = self._get_valid_directions()

        if not valid_directions:
            return self._direction

        current_x, current_y = self._get_current_cell()
        pacman_x, pacman_y = pacman_cell

        best_direction = valid_directions[0]
        best_distance = -1

        for direction in valid_directions:
            next_x, next_y = self._pathfinder.get_next_cell(
                (current_x, current_y),
                direction,
            )

            distance = abs(next_x - pacman_x) + abs(next_y - pacman_y)

            if distance > best_distance:
                best_distance = distance
                best_direction = direction

        return best_direction

    def eat(self) -> None:
        self._state.eat()
        self.set_speed_multiplier(self._normal_speed_multiplier)

    def is_eaten(self) -> bool:
        return self._state.is_eaten

    def set_blinking(self, is_blinking: bool) -> None:
        self._state.set_blinking(is_blinking)
