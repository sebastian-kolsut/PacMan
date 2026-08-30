from mazegenerator import MazeGenerator
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Dict


_DEFAULT_WIDTH = 15
_DEFAULT_HEIGHT = 15
_MIN_WIDTH = 15
_MIN_HEIGHT = 15
_MAX_WIDTH = 50
_MAX_HEIGHT = 50

_DEFAULT_HIGHSCORE_FILENAME = "highscores.json"
_DEFAULT_LIVES = 3
_DEFAULT_POINTS_PER_PACGUM = 10
_DEFAULT_POINTS_PER_SUPER_PACGUM = 50
_DEFAULT_POINTS_PER_GHOST = 100
_DEFAULT_SEED = 42
_DEFAULT_LEVEL_MAX_TIME = 180
_DEFAULT_PACGUM = 50

_SUPER_PACGUM_CORNERS = 4
_ALL_WALLS = 0b1111


class LevelModel(BaseModel):
    """Validated settings for a single level, clamped to safe defaults.

    Attributes:
        width: Maze width in cells.
        height: Maze height in cells.
        pacgum: Number of regular pacgums to place in the maze.
        level_max_time: Seconds available to finish the level.
    """

    width: int = _DEFAULT_WIDTH
    height: int = _DEFAULT_HEIGHT
    pacgum: int = _DEFAULT_PACGUM
    level_max_time: int = _DEFAULT_LEVEL_MAX_TIME

    @field_validator("width", mode="before")
    def set_width_if_invalid(cls, value: int) -> int:
        """Clamp width to the default if it is not a valid cell count.

        Args:
            value: Raw width value from the config file.

        Returns:
            value unchanged if it is an int in (8, 50], otherwise
            _DEFAULT_WIDTH.
        """
        if (
            not isinstance(value, int)
            or value < _MIN_WIDTH
            or value > _MAX_WIDTH
        ):
            print(
                "Error: Invalid width - "
                f"clamped to safe default {_DEFAULT_WIDTH}"
            )
            return _DEFAULT_WIDTH
        return value

    @field_validator("height", mode="before")
    def set_height_if_invalid(cls, value: int) -> int:
        """Clamp height to the default if it is not a valid cell count.

        Args:
            value: Raw height value from the config file.

        Returns:
            value unchanged if it is an int in (8, 50], otherwise
            _DEFAULT_HEIGHT.
        """
        if (
            not isinstance(value, int)
            or value < _MIN_HEIGHT
            or value > _MAX_HEIGHT
        ):
            print(
                "Error: Invalid height - "
                f"clamped to safe default {_DEFAULT_HEIGHT}"
            )
            return _DEFAULT_HEIGHT
        return value

    @field_validator("level_max_time", mode="before")
    def set_level_max_time_if_invalid(cls, value: int) -> int:
        """Clamp level_max_time to the default if it is out of range.

        Args:
            value: Raw level_max_time value from the config file.

        Returns:
            value unchanged if it is an int in (0, 3600], otherwise
            _DEFAULT_LEVEL_MAX_TIME.
        """
        if not isinstance(value, int) or value <= 0 or value > 3600:
            print("Error: Invalid level_max_time - " +
                  f"clamped to safe default {_DEFAULT_LEVEL_MAX_TIME}")
            return _DEFAULT_LEVEL_MAX_TIME
        return value

    @model_validator(mode="after")
    def set_pacgum_if_invalid(self) -> "LevelModel":
        """Clamp pacgum to the maze's actual pacgum capacity.

        Generates a sample maze at this level's width/height to count how
        many cells can actually hold a pacgum (excluding fully-walled
        pattern cells and the four super-pacgum corners), then clamps
        pacgum to that capacity if it is invalid or too high.

        Returns:
            This LevelModel, with pacgum clamped if necessary.
        """
        # Pattern-cell count depends only on maze size, not seed.
        mazegen = MazeGenerator(
            (self.width, self.height), perfect=False, seed=_DEFAULT_SEED)
        pattern_cells = sum(
            1
            for row in mazegen.maze
            for cell in row
            if cell == _ALL_WALLS
        )
        capacity = self.width * self.height - pattern_cells \
            - _SUPER_PACGUM_CORNERS

        if self.pacgum <= 0 or self.pacgum > capacity:
            print("Error: Invalid pacgum - " +
                  f"clamped to safe default {capacity}")
            self.pacgum = capacity

        return self

    @field_validator("pacgum", mode="before")
    def set_pacgum_type_if_invalid(cls, value: object) -> int:
        """Validate pacgum type and replace invalid
            values with a safe default."""
        if not isinstance(value, int):
            print(
                "Error: Invalid pacgum - "
                f"clamped to safe default {_DEFAULT_PACGUM}"
            )
            return _DEFAULT_PACGUM
        return value


_DEFAULT_LEVELS = [
    LevelModel(width=15, height=15),
    LevelModel(width=18, height=18),
    LevelModel(width=20, height=20),
    LevelModel(width=22, height=22),
    LevelModel(width=25, height=25),
    LevelModel(width=28, height=25),
    LevelModel(width=30, height=25),
    LevelModel(width=32, height=28),
    LevelModel(width=35, height=30),
    LevelModel(width=38, height=32),
]


class Config(BaseModel):
    """Validated top-level game configuration, clamped to safe defaults.

    Attributes:
        highscore_filename: Path to the JSON highscores file.
        lives: Starting number of lives.
        points_per_pacgum: Points earned for eating a regular pacgum.
        points_per_super_pacgum: Points earned for eating a super pacgum.
        points_per_ghost: Points earned for eating a frightened ghost.
        seed: Random seed used to generate the first level's maze.
        levels: Per-level settings, one entry per level.
    """

    highscore_filename: str = _DEFAULT_HIGHSCORE_FILENAME
    lives: int = _DEFAULT_LIVES
    points_per_pacgum: int = _DEFAULT_POINTS_PER_PACGUM
    points_per_super_pacgum: int = _DEFAULT_POINTS_PER_SUPER_PACGUM
    points_per_ghost: int = _DEFAULT_POINTS_PER_GHOST
    seed: int = _DEFAULT_SEED
    levels: List[LevelModel] = _DEFAULT_LEVELS

    @field_validator("highscore_filename", mode="before")
    def set_highscore_filename_if_invalid(cls, value: str) -> str:
        """Clamp highscore_filename to the default if it is not a .json path.

        Args:
            value: Raw highscore_filename value from the config file.

        Returns:
            value unchanged if it is a string ending in ".json", otherwise
            _DEFAULT_HIGHSCORE_FILENAME.
        """
        if not isinstance(value, str) or not value.endswith(".json"):
            print("Error: Invalid highscore_filename - " +
                  f"clamped to safe default {_DEFAULT_HIGHSCORE_FILENAME}")
            return _DEFAULT_HIGHSCORE_FILENAME
        return value

    @field_validator("lives", mode="before")
    def set_lives_if_invalid(cls, value: int) -> int:
        """Clamp lives to the default if it is not a positive integer.

        Args:
            value: Raw lives value from the config file.

        Returns:
            value unchanged if it is a positive int, otherwise
            _DEFAULT_LIVES.
        """
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid lives - " +
                  f"clamped to safe default {_DEFAULT_LIVES}")
            return _DEFAULT_LIVES
        return value

    @field_validator("points_per_pacgum", mode="before")
    def set_points_per_pacgum_if_invalid(cls, value: int) -> int:
        """Clamp points_per_pacgum to the default if it is out of range.

        Args:
            value: Raw points_per_pacgum value from the config file.

        Returns:
            value unchanged if it is an int in (0, 200], otherwise
            _DEFAULT_POINTS_PER_PACGUM.
        """
        if not isinstance(value, int) or value <= 0 or value > 200:
            print("Error: Invalid points_per_pacgum - " +
                  f"clamped to safe default {_DEFAULT_POINTS_PER_PACGUM}")
            return _DEFAULT_POINTS_PER_PACGUM
        return value

    @field_validator("points_per_super_pacgum", mode="before")
    def set_points_per_super_pacgum_if_invalid(cls, value: int) -> int:
        """Clamp points_per_super_pacgum to the default if out of range.

        Args:
            value: Raw points_per_super_pacgum value from the config file.

        Returns:
            value unchanged if it is an int in (0, 1000], otherwise
            _DEFAULT_POINTS_PER_SUPER_PACGUM.
        """
        if not isinstance(value, int) or value <= 0 or value > 1000:
            print(
                "Error: Invalid points_per_super_pacgum - " +
                f"clamped to safe default {_DEFAULT_POINTS_PER_SUPER_PACGUM}")
            return _DEFAULT_POINTS_PER_SUPER_PACGUM
        return value

    @field_validator("points_per_ghost", mode="before")
    def set_points_per_ghost_if_invalid(cls, value: int) -> int:
        """Clamp points_per_ghost to the default if it is out of range.

        Args:
            value: Raw points_per_ghost value from the config file.

        Returns:
            value unchanged if it is an int in (0, 3000], otherwise
            _DEFAULT_POINTS_PER_GHOST.
        """
        if not isinstance(value, int) or value <= 0 or value > 3000:
            print("Error: Invalid points_per_ghost - " +
                  f"clamped to safe default {_DEFAULT_POINTS_PER_GHOST}")
            return _DEFAULT_POINTS_PER_GHOST
        return value

    @field_validator("seed", mode="before")
    def set_seed_if_invalid(cls, value: int) -> int:
        """Clamp seed to the default if it is not an integer.

        Args:
            value: Raw seed value from the config file.

        Returns:
            value unchanged if it is an int, otherwise _DEFAULT_SEED.
        """
        if not isinstance(value, int):
            print("Error: Invalid seed - " +
                  f"clamped to safe default {_DEFAULT_SEED}")
            return _DEFAULT_SEED
        return value

    @field_validator("levels", mode="before")
    def set_level_if_invalid(
            cls, value: List[Dict[str, int]]
            ) -> List[LevelModel] | List[Dict[str, int]]:
        """Clamp levels to the default list if it is missing or empty.

        Args:
            value: Raw levels value from the config file.

        Returns:
            value unchanged if it is a non-empty list, otherwise
            _DEFAULT_LEVELS.
        """
        if not isinstance(value, list) or not value:
            print("Error: Invalid levels - clamped to safe default for levels")
            return _DEFAULT_LEVELS

        if len(value) < 10:
            print("Error: Fewer than 10 levels - extending with safe defaults")
            return value + _DEFAULT_LEVELS[len(value):]

        return value
