from src.models.dataclasses import MlxContext


class MainMenu:
    """Render and handle the main menu screen."""

    def __init__(self, mlx_ctx: MlxContext) -> None:
        self._mlx_ctx = mlx_ctx

    def render(self) -> None:
        m = self._mlx_ctx.m

        m.mlx_clear_window(self._mlx_ctx.mlx_ptr, self._mlx_ctx.win_ptr)

        center_x = self._mlx_ctx.win_width // 2
        center_y = self._mlx_ctx.win_height // 2

        m.mlx_string_put(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            center_x - 80,
            center_y - 60,
            0xFFFF00,
            "PAC-MAN",
        )
        m.mlx_string_put(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            center_x - 130,
            center_y,
            0xFFFFFF,
            "Press SPACE to start",
        )
        m.mlx_string_put(
            self._mlx_ctx.mlx_ptr,
            self._mlx_ctx.win_ptr,
            center_x - 130,
            center_y + 30,
            0xFFFFFF,
            "Press ESC to exit",
        )
