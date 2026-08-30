from mazegenerator import MazeGenerator
from src.models import Config
from src.models import Direction
from dataclasses import dataclass
from typing import Set
import random


_UP = 0
_RIGHT = 1
_DOWN = 2
_LEFT = 3

_RANDOM_SEED_RANGE = (1, 1_000_000)


@dataclass
class Bitboards:
    """Per-direction bitboards: bit i of each field is set if cell i has
    a wall on that side.

    Attributes:
        up: Bitboard of cells with a wall on their top side.
        right: Bitboard of cells with a wall on their right side.
        down: Bitboard of cells with a wall on their bottom side.
        left: Bitboard of cells with a wall on their left side.
    """

    up: int = 0
    right: int = 0
    down: int = 0
    left: int = 0


class Maze:
    """Generates a maze via the A-Maze-ing package and exposes its walls
    as bitboards for fast collision lookups."""

    def __init__(self, config: Config):
        """Generate the first level's maze.

        Args:
            config: Game configuration, used for the per-level maze size
                and the fixed seed for the first level.
        """
        self.config = config
        self.level = 0
        self.bitboards = Bitboards()
        self.dirty = False

        self.generate_new_maze()

    def generate_new_maze(self) -> None:
        """Generate a new maze for the current level into the bitboards.

        Uses the config's fixed seed for level 0, and a random seed for
        every subsequent level.
        """
        self.width = self.config.levels[self.level].width
        self.height = self.config.levels[self.level].height
        seed = self.config.seed if self.level == 0 \
            else random.randint(*_RANDOM_SEED_RANGE)
        mazegen = MazeGenerator(
            (self.width, self.height),
            perfect=False,
            seed=seed,
        )

        self._reset_bitboard()

        for y in range(self.height):
            for x in range(self.width):
                self._set_cell_value(x, y, mazegen, self.width)

        self.dirty = False
        self.patters_positions = self._load_42_patern_positions()

    def is_wall_up(self, bit_idx: int) -> bool:
        """Return whether the cell at bit_idx has a wall on its top side.

        Args:
            bit_idx: Cell index, as y * width + x.
        """
        return (self.bitboards.up & (1 << bit_idx)) != 0

    def is_wall_right(self, bit_idx: int) -> bool:
        """Return whether the cell at bit_idx has a wall on its right side.

        Args:
            bit_idx: Cell index, as y * width + x.
        """
        return (self.bitboards.right & (1 << bit_idx)) != 0

    def is_wall_down(self, bit_idx: int) -> bool:
        """Return whether the cell at bit_idx has a wall on its bottom side.

        Args:
            bit_idx: Cell index, as y * width + x.
        """
        return (self.bitboards.down & (1 << bit_idx)) != 0

    def is_wall_left(self, bit_idx: int) -> bool:
        """Return whether the cell at bit_idx has a wall on its left side.

        Args:
            bit_idx: Cell index, as y * width + x.
        """
        return (self.bitboards.left & (1 << bit_idx)) != 0

    def is_wall_direction(self, bit_idx: int, direction: Direction) -> bool:
        """Return whether the cell at bit_idx has a wall in direction.

        Args:
            bit_idx: Cell index, as y * width + x.
            direction: Side of the cell to check.

        Returns:
            True if there is a wall on that side, False otherwise (also
            False for any value outside the four cardinal directions).
        """
        match direction:
            case Direction.UP:
                return self.is_wall_up(bit_idx)
            case Direction.RIGHT:
                return self.is_wall_right(bit_idx)
            case Direction.DOWN:
                return self.is_wall_down(bit_idx)
            case Direction.LEFT:
                return self.is_wall_left(bit_idx)

        return False

    def _load_42_patern_positions(self) -> Set[int]:
        """Return the indices of every cell walled in on all four sides.

        These fully-enclosed cells are used to draw the decorative "42"
        pattern in the maze walls.

        Returns:
            The set of cell indices with a wall on every side.
        """
        positions: Set[int] = set()

        for idx in range(self.width * self.height):
            if self.is_wall_up(idx) and self.is_wall_right(idx) \
                    and self.is_wall_down(idx) and self.is_wall_left(idx):
                positions.add(idx)

        return positions

    def _set_cell_value(self, x: int, y: int, mazegen: MazeGenerator,
                        width: int) -> None:
        """Copy one cell's walls from the generator into the bitboards.

        Args:
            x: Cell column.
            y: Cell row.
            mazegen: Generated maze to read the cell's walls from.
            width: Maze width, used to compute the bit position.
        """
        bit_pos = y * width + x

        if (mazegen.maze[y][x] & (1 << Direction.UP)) != 0:
            self.bitboards.up |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << Direction.RIGHT)) != 0:
            self.bitboards.right |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << Direction.DOWN)) != 0:
            self.bitboards.down |= (1 << bit_pos)
        if (mazegen.maze[y][x] & (1 << Direction.LEFT)) != 0:
            self.bitboards.left |= (1 << bit_pos)

    def _reset_bitboard(self) -> None:
        """Clear every wall bitboard back to zero."""
        self.bitboards.up = 0
        self.bitboards.right = 0
        self.bitboards.down = 0
        self.bitboards.left = 0
