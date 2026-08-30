import numpy as np

from src.screens.draw_utils import FrameBuffer


def _opaque_tile(width: int, height: int, color: int = 200) -> np.ndarray:
    tile = np.zeros((height, width, 4), dtype=np.uint8)
    tile[:, :, :3] = color
    tile[:, :, 3] = 255
    return tile


def test_draw_blended_tile_fully_inside_bounds_draws_whole_tile() -> None:
    pixels = np.zeros((10, 10, 4), dtype=np.uint8)
    pixels[:, :, 3] = 255
    tile = _opaque_tile(4, 4)

    FrameBuffer.draw_blended_tile(pixels, tile, 2, 2)

    assert np.all(pixels[2:6, 2:6, :3] == 200)
    assert np.all(pixels[0:2, :, :3] == 0)


def test_draw_blended_tile_clips_instead_of_raising_when_too_wide() -> None:
    pixels = np.zeros((10, 10, 4), dtype=np.uint8)
    pixels[:, :, 3] = 255
    wide_tile = _opaque_tile(20, 4)

    FrameBuffer.draw_blended_tile(pixels, wide_tile, 5, 2)

    assert np.all(pixels[2:6, 5:10, :3] == 200)


def test_draw_blended_tile_clips_when_position_is_negative() -> None:
    pixels = np.zeros((10, 10, 4), dtype=np.uint8)
    pixels[:, :, 3] = 255
    tile = _opaque_tile(4, 4)

    FrameBuffer.draw_blended_tile(pixels, tile, -2, -2)

    assert np.all(pixels[0:2, 0:2, :3] == 200)


def test_draw_blended_tile_no_overlap_is_a_noop() -> None:
    pixels = np.zeros((10, 10, 4), dtype=np.uint8)
    pixels[:, :, 3] = 255
    tile = _opaque_tile(4, 4)

    FrameBuffer.draw_blended_tile(pixels, tile, 100, 100)

    assert np.all(pixels[:, :, :3] == 0)


def test_draw_clipped_crops_tile_to_destination_bounds() -> None:
    pixels = np.zeros((10, 10, 4), dtype=np.uint8)
    wide_tile = _opaque_tile(20, 4)

    FrameBuffer.draw_clipped(pixels, wide_tile, 5, 2)

    assert np.all(pixels[2:6, 5:10, :3] == 200)
    assert np.all(pixels[2:6, 5:10, 3] == 255)
