from pydantic import BaseModel, RootModel, ValidationError
from typing import List


_MAX_ENTRIES = 10
_MAX_NAME_LENGHT = 10


class NameToLongError(Exception):
    """Raised when a highscore name exceeds the maximum allowed length."""

    def __init__(self) -> None:
        """Initialize the error with its fixed message."""
        super().__init__("Name is to long - max 10 characters.")


class NotAlphanumericError(Exception):
    """Raised when a highscore name contains disallowed characters."""

    def __init__(self) -> None:
        """Initialize the error with its fixed message."""
        super().__init__("Name contains other characters than alphanumerc \
            and spaces.")


class NegativeScoreError(Exception):
    """Raised when a highscore's score is negative."""

    def __init__(self) -> None:
        """Initialize the error with its fixed message."""
        super().__init__("Score must be a non-negative integer.")


class HighscoreData(BaseModel):
    """A single highscore entry: a player name and their score."""

    name: str
    score: int


class HighscoresList(RootModel):
    """A pydantic root model wrapping the ordered list of highscores."""

    root: List[HighscoreData]


class Highscores:
    """Loads, validates and persists the top-10 highscore leaderboard."""

    def __init__(self, file_name: str):
        """Load the leaderboard from disk, creating it if needed.

        Args:
            file_name: Path to the JSON highscores file. If missing or
                invalid, an empty leaderboard is used and a new file is
                created at this path (best-effort; persistence is skipped
                if the path cannot be written to).
        """
        self._file_name = file_name

        try:
            self._highscores = self._load_file()
        except (FileNotFoundError, ValidationError):
            self._highscores = HighscoresList([])
            try:
                self.write_scores()
            except OSError as error:
                print(
                    "Error: Could not create highscore file "
                    f"'{self._file_name}': {error}. "
                    "Continuing without persistent highscores."
                )
        self._highscores.root.sort(key=lambda x: x.score, reverse=True)

    def add_score(self, name: str, score: int) -> None:
        """Insert a new highscore, keeping only the top 10 entries.

        Args:
            name: Player name (alphanumeric characters and spaces only,
                at most 10 characters).
            score: Non-negative score to record.

        Raises:
            NotAlphanumericError: If name contains disallowed characters.
            NameToLongError: If name is longer than 10 characters.
            NegativeScoreError: If score is negative.
        """
        temp_name = name.replace(" ", "a")

        if not temp_name.isalnum():
            raise NotAlphanumericError
        if len(temp_name) > _MAX_NAME_LENGHT:
            raise NameToLongError
        if score < 0:
            raise NegativeScoreError

        self._highscores.root.append(HighscoreData(name=name, score=score))
        self._highscores.root.sort(key=lambda x: x.score, reverse=True)
        del self._highscores.root[_MAX_ENTRIES:]

    def write_scores(self) -> None:
        """Persist the current leaderboard to the highscores file."""
        json_str = self._highscores.model_dump_json(indent=2)

        with open(self._file_name, "w") as f:
            f.write(json_str)

    def get_leaderboard(self) -> HighscoresList:
        """Return the current leaderboard, sorted highest score first."""
        return self._highscores

    def is_score_eligible(self, score: int) -> bool:
        """Return whether score would make it onto the top-10 leaderboard.

        Args:
            score: Score to check.

        Returns:
            True if the leaderboard has fewer than 10 entries, or if score
            beats the current lowest entry.
        """
        if len(self._highscores.root) < _MAX_ENTRIES:
            return True
        return score > self._highscores.root[-1].score

    def _load_file(self) -> HighscoresList:
        """Read and validate the highscores file from disk.

        Returns:
            The parsed leaderboard.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValidationError: If the file's contents are not a valid
                highscores list.
        """
        with open(self._file_name, "r") as f:
            highscores = f.read()

        return HighscoresList.model_validate_json(highscores)
