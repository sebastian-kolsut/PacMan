from src.models.dataclasses import MlxContext
from src.models import Config
from src.screens.draw_utils import DrawMaze
from src.screens.Maze import Maze


class PlayGame:
    def __init__(self, mlx_ctx: MlxContext, config: Config) -> None:
        self._mlx_ctx = mlx_ctx
        self._current_level = 0
        self._config = config
        self._maze = Maze(config)
        self._draw_maze = DrawMaze(mlx_ctx, self._maze)

    def render(self) -> None:
        self._draw_maze.draw()
        self._mlx_ctx.m.mlx_put_image_to_window(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            self._draw_maze.get_img_ptr(), self._draw_maze.get_maze_position(),
            0)
