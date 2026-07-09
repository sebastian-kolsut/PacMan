from src.models import Config, MlxContext
from src.screens.game import RenderMaze, Maze, PacMan, Pacgums
from src.screens.draw_utils import FrameBuffer

from Xlib.display import Display  # type: ignore[import-untyped]


_W, _A, _S, _D = 119, 97, 115, 100
_A_UP, _A_RIGHT, _A_DOWN, _A_LEFT = 65362, 65363, 65364, 65361
_DIRECTION_KEYS = (_W, _A, _S, _D,
                   _A_UP, _A_RIGHT, _A_DOWN, _A_LEFT)


class PlayGame:
    def __init__(self, mlx_ctx: MlxContext, config: Config) -> None:
        self._mlx_ctx = mlx_ctx
        self._current_level = 0
        self._config = config
        self._maze = Maze(config)
        self._render_maze = RenderMaze(mlx_ctx, self._maze)
        cell_size = self._render_maze.get_cell_size()
        self._pacgums = Pacgums(cell_size, mlx_ctx, self._maze, config.pacgum)
        self._pac_man = PacMan(cell_size, mlx_ctx, self._maze, self._pacgums)
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._last_pressed_key = 0

        self._keyboard = Display()
        self._direction_keycodes = {
            key: self._keyboard.keysym_to_keycode(key)
            for key in _DIRECTION_KEYS
        }

    def _get_pressed_direction(self) -> int:
        keymap = self._keyboard.query_keymap()
        for key in _DIRECTION_KEYS:
            keycode = self._direction_keycodes[key]
            if keymap[keycode // 8] & (1 << (keycode % 8)):
                return key
        return 0

    def update(self, difference: float) -> None:
        self._pac_man.update(difference, self._get_pressed_direction())

    def render(self) -> None:
        maze_img = self._render_maze.render()
        pac_img = self._pac_man.render()

        pixels = self._fb.get_array()
        pixels[:, :] = [0, 0, 0, 0]

        maze_x = self._render_maze.get_maze_position()

        self._fb.draw_blended_tile(pixels, maze_img, 0,
                                   maze_x)
        self._pacgums.draw_pacgums_to_image(pixels, maze_x)
        self._fb.draw_blended_tile(
            pixels, pac_img,
            int(self._pac_man._pos_y) + self._pac_man._offset,
            int(self._pac_man._pos_x) + self._pac_man._offset + maze_x
            )

        self._fb.commit()
        self._fb.put_image_to_window()
