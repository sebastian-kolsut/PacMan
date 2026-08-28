from typing import NamedTuple, Tuple

BGRA = Tuple[int, int, int, int]


class WallTheme(NamedTuple):
    name: str
    base_color: BGRA
    pattern_color: BGRA


WALL_THEMES = [
    WallTheme("Purple", (157, 63, 253, 220), (218, 180, 255, 210)),
    WallTheme("Pink", (255, 184, 219, 255), (255, 184, 219, 165)),
    WallTheme("Ice Blue", (255, 150, 60, 230), (255, 205, 150, 210)),
    WallTheme("Toxic Green", (60, 220, 90, 225), (150, 255, 170, 205)),
]
