from src.dataclasses import MlxContext
from src.models import Config


class PlayGame:
    def __init__(self, mlx: MlxContext, config: Config) -> None:
        self._mlx = mlx
        self.current_level = 0
        self.config = config

    def render(self) -> None:
        pass
