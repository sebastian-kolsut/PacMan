from src.dataclasses import MlxContext
from src.models import Config


class DrawMaze:

    def __init__(self, mlx_ctx: MlxContext, config: Config):
        self.mlx_ctx = mlx_ctx
        self.config = config

    def draw(self) -> None:
        img_ptr = \
            self.mlx_ctx.m.mlx_new_image(self.mlx_ctx.win_ptr, width, height)
        data, bpp, size_line, img_format = m.mlx_get_data_addr(img_ptr)

    def _get_maze_size_pixels(self) -> None:
        win_width, win_height = \
            self.mlx_ctx.m.mlx_get_screen_size(self.mlx_ctx.mlx_ptr)[1:]
