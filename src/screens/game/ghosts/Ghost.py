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
_MIN_SPEED_MULTIPLIER = 1.2
_MAX_SPEED_MULTIPLIER = 5.0
_FRIGHTENED_SPEED_MULTIPLIER = 1.3


class Ghost(Character):
    """Base ghost behavior: movement, frightened/eaten state and rendering.

    Subclasses (Blinky, Pinky, Inky, Clyde) each override
    _choose_direction (and usually _should_recalculate_direction) to
    implement their own chase behavior.
    """

    def __init__(
        self,
        cell_size: int,
        mlx_ctx: MlxContext,
        maze: Maze,
        asset_name: str,
        start_cell: Tuple[int, int],
        speed_multiplier: float = _DEFAULT_SPEED_MULTIPLIER,
    ) -> None:
        """Spawn the ghost at start_cell and load its sprites.

        Args:
            cell_size: Size in pixels of one maze cell.
            mlx_ctx: Window/rendering context used for the sprite buffer.
            maze: Maze the ghost moves through.
            asset_name: Key into _GHOST_ASSETS selecting this ghost's
                normal-mode sprite.
            start_cell: (x, y) cell to spawn in and respawn to.
            speed_multiplier: Normal-mode speed, in cells per second.
        """
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
        """Advance the ghost's state and movement for one frame.

        Args:
            delta_time: Seconds elapsed since the last update.
            pacman_cell: Pac-Man's current (x, y) cell, used to chase or
                flee from.
            pacman_direction: Pac-Man's current facing direction.
        """
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
        """Return whether to re-evaluate direction at every cell center.

        Overridden by subclasses; the base ghost only reconsiders its
        direction when it hits a wall or a dead end.
        """
        return False

    def render(self) -> NDArray:
        """Render and return the ghost's current sprite frame.

        Returns:
            A blank (fully transparent) image while eaten, the blue
            frightened sprite (blinking near the end of frightened mode),
            or the ghost's normal sprite otherwise.
        """
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
        """Return the (y, x) pixel position to draw the ghost's sprite at."""
        return (
            int(self._pos_y) + self._offset,
            int(self._pos_x) + self._offset,
        )

    def _choose_direction(
        self,
        pacman_cell: Tuple[int, int],
        pacman_direction: Direction,
    ) -> Direction:
        """Pick the next movement direction while chasing (default: random).

        Overridden by every subclass to implement its own chase strategy.

        Args:
            pacman_cell: Pac-Man's current (x, y) cell.
            pacman_direction: Pac-Man's current facing direction.

        Returns:
            A valid direction to move in, or the current direction if
            none are available.
        """
        valid_directions = self._get_valid_directions()

        if valid_directions:
            return choice(valid_directions)

        return self._direction

    def _choose_bfs_direction(self, target_cell: Tuple[int, int]) -> Direction:
        """Return the first step direction of the shortest path to a cell.

        Args:
            target_cell: (x, y) cell to path toward.

        Returns:
            The direction toward target_cell, falling back to the current
            direction (if still valid) or a random valid direction when
            no path exists.
        """
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
        """Return the directions the ghost can currently move in."""
        return self._pathfinder.get_valid_directions(
            self._get_current_cell(),
        )

    def _get_random_valid_direction(self) -> Direction:
        """Return a random direction the ghost can currently move in.

        Returns:
            A random valid direction, or Direction.RIGHT if none exist.
        """
        valid_directions = self._get_valid_directions()
        if valid_directions:
            return choice(valid_directions)
        return Direction.RIGHT

    def set_speed_multiplier(self, speed_multiplier: float) -> None:
        """Set the ghost's movement speed, clamped to a safe range.

        Args:
            speed_multiplier: Desired speed, in cells per second.
        """
        speed_multiplier = max(
            _MIN_SPEED_MULTIPLIER,
            min(speed_multiplier, _MAX_SPEED_MULTIPLIER),
        )
        self._speed = self._cell_size * speed_multiplier

    def get_speed_multiplier(self) -> float:
        """Return the ghost's current speed, in cells per second."""
        return self._speed / self._cell_size

    def _get_random_reachable_cell(self) -> Tuple[int, int]:
        """Return a random cell reachable from the ghost's current cell.

        Returns:
            A random reachable cell other than the current one, or the
            current cell if it has no other reachable cells.
        """
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
        """Enter or leave frightened mode and adjust speed accordingly.

        Args:
            is_frightened: True to make the ghost edible and slow it
                down, False to return it to normal speed. Ignored while
                the ghost is eaten.
        """
        if self._state.is_eaten:
            return

        self._state.set_frightened(is_frightened)

        if is_frightened:
            self.set_speed_multiplier(_FRIGHTENED_SPEED_MULTIPLIER)
        else:
            self.set_speed_multiplier(self._normal_speed_multiplier)

    def is_frightened(self) -> bool:
        """Return whether the ghost is currently edible by Pac-Man."""
        return self._state.is_frightened

    def _choose_flee_direction(
        self,
        pacman_cell: Tuple[int, int],
    ) -> Direction:
        """Pick a direction that moves the ghost away from Pac-Man.

        Args:
            pacman_cell: Pac-Man's current (x, y) cell to flee from.

        Returns:
            The direction toward the reachable cell farthest from
            pacman_cell, or a valid direction chosen at random if no
            other reachable cell exists.
        """
        current_cell = self._get_current_cell()
        reachable_cells = self._pathfinder.get_reachable_cells(current_cell)

        if len(reachable_cells) <= 1:
            valid_directions = self._get_valid_directions()
            if valid_directions:
                return choice(valid_directions)
            return self._direction

        reachable_cells = [
            cell
            for cell in reachable_cells
            if cell != current_cell
        ]

        pacman_x, pacman_y = pacman_cell

        target_cell = max(
            reachable_cells,
            key=lambda cell: (
                abs(cell[0] - pacman_x)
                + abs(cell[1] - pacman_y)
            ),
        )

        return self._choose_bfs_direction(target_cell)

    def eat(self) -> None:
        """Mark the ghost as eaten and reset its speed to normal."""
        self._state.eat()
        self.set_speed_multiplier(self._normal_speed_multiplier)

    def is_eaten(self) -> bool:
        """Return whether the ghost has been eaten and is respawning."""
        return self._state.is_eaten

    def set_blinking(self, is_blinking: bool) -> None:
        """Start or stop the frightened-mode blinking warning.

        Args:
            is_blinking: True to start alternating the sprite, False to
                stop.
        """
        self._state.set_blinking(is_blinking)
