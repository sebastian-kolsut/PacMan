from mazegenerator import MazeGenerator  # type: ignore[import-untyped]
from pydantic import BaseModel, field_validator, model_validator
from typing import List, Dict


_DEFAULT_WIDTH = 10
_DEFAULT_HEIGHT = 10

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
    width: int = _DEFAULT_WIDTH
    height: int = _DEFAULT_HEIGHT
    pacgum: int = _DEFAULT_PACGUM
    level_max_time: int = _DEFAULT_LEVEL_MAX_TIME

    @field_validator("width", mode="before")
    def set_width_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid width - " +
                  f"clamped to safe default {_DEFAULT_WIDTH}")
            return _DEFAULT_WIDTH
        return value

    @field_validator("height", mode="before")
    def set_height_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid height - " +
                  f"clamped to safe default {_DEFAULT_HEIGHT}")
            return _DEFAULT_HEIGHT
        return value

    @field_validator("level_max_time", mode="before")
    def set_level_max_time_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid level_max_time - " +
                  f"clamped to safe default {_DEFAULT_LEVEL_MAX_TIME}")
            return _DEFAULT_LEVEL_MAX_TIME
        return value

    @model_validator(mode="after")
    def set_pacgum_if_invalid(self) -> "LevelModel":
        # Pattern-cell count depends only on maze size, not seed.
        mazegen = MazeGenerator(
            (self.width, self.height), seed=_DEFAULT_SEED)
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


_DEFAULT_LEVELS = [
    LevelModel(width=10 + i * 5, height=10 + i * 5) for i in range(10)
]


class Config(BaseModel):
    highscore_filename: str = _DEFAULT_HIGHSCORE_FILENAME
    lives: int = _DEFAULT_LIVES
    points_per_pacgum: int = _DEFAULT_POINTS_PER_PACGUM
    points_per_super_pacgum: int = _DEFAULT_POINTS_PER_SUPER_PACGUM
    points_per_ghost: int = _DEFAULT_POINTS_PER_GHOST
    seed: int = _DEFAULT_SEED
    levels: List[LevelModel] = _DEFAULT_LEVELS

    @field_validator("highscore_filename", mode="before")
    def set_highscore_filename_if_invalid(cls, value: str) -> str:
        if not isinstance(value, str) or not value.endswith(".json"):
            print("Error: Invalid highscore_filename - " +
                  f"clamped to safe default {_DEFAULT_HIGHSCORE_FILENAME}")
            return _DEFAULT_HIGHSCORE_FILENAME
        return value

    @field_validator("lives", mode="before")
    def set_lives_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid lives - " +
                  f"clamped to safe default {_DEFAULT_LIVES}")
            return _DEFAULT_LIVES
        return value

    @field_validator("points_per_pacgum", mode="before")
    def set_points_per_pacgum_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid points_per_pacgum - " +
                  f"clamped to safe default {_DEFAULT_LIVES}")
            return _DEFAULT_LIVES
        return value

    @field_validator("points_per_super_pacgum", mode="before")
    def set_points_per_super_pacgum_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print(
                "Error: Invalid points_per_super_pacgum - " +
                f"clamped to safe default {_DEFAULT_POINTS_PER_SUPER_PACGUM}")
            return _DEFAULT_POINTS_PER_SUPER_PACGUM
        return value

    @field_validator("points_per_ghost", mode="before")
    def set_points_per_ghost_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int) or value <= 0:
            print("Error: Invalid points_per_ghost - " +
                  f"clamped to safe default {_DEFAULT_POINTS_PER_GHOST}")
            return _DEFAULT_POINTS_PER_GHOST
        return value

    @field_validator("seed", mode="before")
    def set_seed_if_invalid(cls, value: int) -> int:
        if not isinstance(value, int):
            print("Error: Invalid seed - " +
                  f"clamped to safe default {_DEFAULT_SEED}")
            return _DEFAULT_SEED
        return value

    @field_validator("levels", mode="before")
    def set_level_if_invalid(
            cls, value: List[Dict[str, int]]
            ) -> List[LevelModel] | List[Dict[str, int]]:
        if not isinstance(value, list) or not value:
            print("Error: Invalid level_max_time - " +
                  "clamped to safe default for levels")
            return _DEFAULT_LEVELS
        return value
