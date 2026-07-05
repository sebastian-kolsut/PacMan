from src.screens.draw_utils import DrawMaze
from src.models.dataclasses import MlxContext
from src.screens.Maze import Maze
from src.Parser import Parser
from mlx import Mlx


def _get_mlx_context() -> MlxContext:
    m = Mlx()
    mlx_ptr = m.mlx_init()
    win_width, win_height = m.mlx_get_screen_size(mlx_ptr)[1:]
    win_ptr = m.mlx_new_window(mlx_ptr, win_width, win_height, "PacMan")
    mlx_ctx = MlxContext(
        m=m,
        mlx_ptr=mlx_ptr,
        win_ptr=win_ptr,
        win_width=win_width,
        win_height=win_height
        )
    return mlx_ctx


def test_get_maze_pos() -> None:
    mlx_ctx = _get_mlx_context()
    mlx_ctx.win_height = 200
    mlx_ctx.win_width = 286
    config = Parser().parse("tests/jsons/valid_no_comments.json")
    maze = Maze(config)

    draw = DrawMaze(mlx_ctx, maze)

    x = draw.get_maze_position()

    assert (x * 2) + draw.fb.width == mlx_ctx.win_width
