from src.screens.draw_utils import FrameBuffer, RenderText
from src.Highscores import Highscores, HighscoresList
from src.models import MlxContext

from numpy.typing import NDArray
import numpy as np


_LABEL_FILE = "assets/menu/highscores_marquee.png"

_Y = 0.38


class HighscoresScreen:
    """Displays the top-10 leaderboard from the main menu."""

    def __init__(self, scores: Highscores, mlx_ctx: MlxContext):
        """Load the marquee label and size the screen to the window.

        Args:
            scores: Highscores leaderboard to display.
            mlx_ctx: Window/rendering context to size the screen to.
        """
        self._render_txt = RenderText("assets/fonts/ByteBounce.ttf",
                                      mlx_ctx, 0.07)
        self._scores = scores
        self._fb = FrameBuffer(mlx_ctx, mlx_ctx.win_width, mlx_ctx.win_height)
        self._mlx_ctx = mlx_ctx
        self._label_img = self._fb.get_image_array(
            _LABEL_FILE, mlx_ctx.win_width, mlx_ctx.win_height)
        self._txt_height = self._render_txt.get_text_height()

    def render(self) -> None:
        """Draw the marquee background and the leaderboard rows."""
        frame = self._fb.get_array()
        frame[:, :] = np.array([0, 0, 0, 255], dtype=np.uint8)

        self._fb.draw_blended_tile(frame, self._label_img, 0, 0)
        self._put_text_to_image(frame)

        self._fb.commit()
        self._fb.put_image_to_window()

    def _put_text_to_image(self, frame: NDArray[np.uint8]) -> None:
        """Draw the leaderboard's positions, names and scores onto frame.

        Args:
            frame: Destination pixel buffer to draw onto.
        """
        leaderboard = self._scores.get_leaderboard()

        center_x = self._mlx_ctx.win_width // 2
        y = int(self._mlx_ctx.win_height * _Y)

        dot_pos_x = \
            self._put_positions_img(len(leaderboard.root), frame, center_x, y)
        self._put_names_img(frame, y, leaderboard, dot_pos_x)
        self._put_scores_img(frame, y, leaderboard, center_x)

    def _put_positions_img(self, num_records: int, img: NDArray[np.uint8],
                           center: int, y: int) -> int:
        """Draw the "1.", "2.", ... rank column for each leaderboard row.

        Args:
            num_records: Number of leaderboard rows to draw ranks for.
            img: Destination pixel buffer to draw onto.
            center: X coordinate of the screen's horizontal center.
            y: Y coordinate of the first row.

        Returns:
            The x coordinate the rank column was right-aligned to, used
            to position the name column next to it.
        """
        dot_x_pos = int(center - self._mlx_ctx.win_width * 0.2)

        for i in range(1, num_records + 1):
            position = f"{i}."
            txt = self._render_txt.put_text_to_image(position)
            txt_width = self._render_txt.get_text_width(position)
            self._fb.draw_blended_tile(img, txt, dot_x_pos - txt_width, y)
            y += self._txt_height

        return dot_x_pos

    def _put_names_img(self, img: NDArray[np.uint8], y: int,
                       records: HighscoresList, dot_pos_x: int) -> None:
        """Draw the player name column for each leaderboard row.

        Args:
            img: Destination pixel buffer to draw onto.
            y: Y coordinate of the first row.
            records: Leaderboard entries to draw names for.
            dot_pos_x: X coordinate the rank column ends at.
        """
        names_x = dot_pos_x + int(self._mlx_ctx.win_width * 0.01)

        for record in records.root:
            txt = self._render_txt.put_text_to_image(record.name)
            self._fb.draw_blended_tile(img, txt, names_x, y)
            y += self._txt_height

    def _put_scores_img(self, img: NDArray[np.uint8], y: int,
                        records: HighscoresList, center: int) -> None:
        """Draw the score column for each leaderboard row.

        Args:
            img: Destination pixel buffer to draw onto.
            y: Y coordinate of the first row.
            records: Leaderboard entries to draw scores for.
            center: X coordinate of the screen's horizontal center.
        """
        scores_x = int(center + self._mlx_ctx.win_width * 0.2)

        for record in records.root:
            txt = self._render_txt.put_text_to_image(str(record.score))
            score_width = self._render_txt.get_text_width(str(record.score))
            self._fb.draw_blended_tile(img, txt, scores_x - score_width, y)
            y += self._txt_height
