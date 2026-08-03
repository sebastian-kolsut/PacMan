from types import SimpleNamespace

from src.screens.game.RenderMaze import RenderMaze


def _make_render_maze(maze_width: int, maze_height: int,
                      win_width: int, win_height: int) -> RenderMaze:
    render_maze = RenderMaze.__new__(RenderMaze)
    render_maze._maze = SimpleNamespace(  # type: ignore[assignment]
        width=maze_width, height=maze_height)
    render_maze._mlx_ctx = SimpleNamespace(  # type: ignore[assignment]
        win_width=win_width, win_height=win_height)
    return render_maze


def test_get_maze_size_pixels_width_constrained() -> None:
    render_maze = _make_render_maze(maze_width=10, maze_height=5,
                                    win_width=1000, win_height=1000)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert cell_size == 70
    assert maze_width_px == 700
    assert maze_height_px == 350


def test_get_maze_size_pixels_height_constrained() -> None:
    render_maze = _make_render_maze(maze_width=10, maze_height=5,
                                    win_width=1000, win_height=200)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert cell_size == 40
    assert maze_width_px == 400
    assert maze_height_px == 200


def test_get_maze_size_pixels_uses_width_scale() -> None:
    render_maze = _make_render_maze(maze_width=7, maze_height=1,
                                    win_width=1000, win_height=10000)

    _, _, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert cell_size == 100


def test_get_maze_size_pixels_never_exceeds_available_space() -> None:
    render_maze = _make_render_maze(maze_width=13, maze_height=17,
                                    win_width=843, win_height=617)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert maze_width_px <= int(843 * 0.7)
    assert maze_height_px <= 617


def test_get_maze_size_pixels_uses_largest_possible_cell_size() -> None:
    render_maze = _make_render_maze(maze_width=13, maze_height=17,
                                    win_width=843, win_height=617)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert cell_size == 36
    assert maze_width_px == 468
    assert maze_height_px == 612


def test_get_maze_size_pixels_dimensions_are_exact_multiples_of_cell_size() \
        -> None:
    render_maze = _make_render_maze(maze_width=9, maze_height=6,
                                    win_width=777, win_height=333)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert maze_width_px == cell_size * 9
    assert maze_height_px == cell_size * 6


def test_get_maze_size_pixels_clamps_cell_size_to_at_least_one() -> None:
    render_maze = _make_render_maze(maze_width=100, maze_height=100,
                                    win_width=5, win_height=5)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert cell_size == 1
    assert maze_width_px == 100
    assert maze_height_px == 100


def test_get_maze_size_pixels_matches_real_window_size() -> None:
    render_maze = _make_render_maze(maze_width=25, maze_height=25,
                                    win_width=1920, win_height=1004)

    maze_width_px, maze_height_px, cell_size = \
        render_maze._get_maze_size_pixels(render_maze._mlx_ctx)

    assert cell_size == 40
    assert maze_width_px == 1000
    assert maze_height_px == 1000
