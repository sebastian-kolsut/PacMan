from src.models.dataclasses import MlxContext
from src.models import Config
from src.screens.draw_utils import RenderMaze
from src.screens.Maze import Maze
from src.screens.PacMan import PacMan
from src.screens.draw_utils import FrameBuffer


class PlayGame:
    def __init__(self, mlx_ctx: MlxContext, config: Config) -> None:
        self._mlx_ctx = mlx_ctx
        self._current_level = 0
        self._config = config
        self._maze = Maze(config)
        self._render_maze = RenderMaze(mlx_ctx, self._maze)
        self._pac_man = PacMan(
            self._render_maze.get_cell_size(), mlx_ctx, self._maze)
        self._key_pressed = 0
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)

    def handle_key_press(self, keycode: int):
        self._key_pressed = keycode

    def update(self, difference: float) -> None:
        self._pac_man.update(difference, self._key_pressed)

    def render(self) -> None:
        maze_img = self._render_maze.render()
        pac_img = self._pac_man.render()

        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]

        maze_x = self._render_maze.get_maze_position()

        self._fb.draw_blended_tile(pixels, maze_img, 0,
                                   maze_x)
        self._fb.draw_blended_tile(
            pixels, pac_img,
            int(self._pac_man._pac_y) + self._pac_man._offset,
            int(self._pac_man._pac_x) + self._pac_man._offset + maze_x
            )

        self._fb.commit()
        self._fb.put_image_to_window()

        # self._mlx_ctx.m.mlx_put_image_to_window(
        #     self._mlx_ctx.mlx_ptr,
        #     self._mlx_ctx.win_ptr,
        #     self._render_maze.get_img_ptr(),
        #     self._render_maze.get_maze_position(),
        #     0)
        # self._mlx_ctx.m.mlx_put_image_to_window(
        #     self._mlx_ctx.mlx_ptr,
        #     self._mlx_ctx.win_ptr,
        #     self._pac_man.get_img_ptr(),
        #     self._pac_man._offset,
        #     self._pac_man._offset - 465)
