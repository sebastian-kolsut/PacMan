from pydantic import BaseModel, RootModel, ValidationError
from typing import List


_MAX_ENTRIES = 10
_MAX_NAME_LENGHT = 10


class NameToLongError(Exception):
    def __init__(self):
        super().__init__("Name is to long - max 10 characters.")


class NotAlphanumericError(Exception):
    def __init__(self):
        super().__init__("Name contains other characters than alphanumerc \
            and spaces.")


class HighscoreData(BaseModel):
    name: str
    score: int


class HighscoresList(RootModel):
    root: List[HighscoreData]


class Highscores:
    def __init__(self, file_name: str):
        self._file_name = file_name

        try:
            self._highscores = self._load_file()
        except (FileNotFoundError, ValidationError):
            self._highscores = HighscoresList([])
            self.write_scores()
        self._highscores.root.sort(key=lambda x: x.score, reverse=True)

    def add_score(self, name: str, score: int) -> None:
        temp_name = name.replace(" ", "a")

        if not temp_name.isalnum():
            raise NotAlphanumericError
        if len(temp_name) > _MAX_NAME_LENGHT:
            raise NameToLongError

        self._highscores.root.append(HighscoreData(name=name, score=score))
        self._highscores.root.sort(key=lambda x: x.score, reverse=True)
        del self._highscores.root[_MAX_ENTRIES:]

    def write_scores(self) -> None:
        json_str = self._highscores.model_dump_json(indent=2)

        with open(self._file_name, "w") as f:
            f.write(json_str)

    def get_leaderboard(self) -> HighscoresList:
        return self._highscores

    def is_score_eligible(self, score: int) -> bool:
        return score > self._highscores.root[-1].score or \
            len(self._highscores.root) < _MAX_ENTRIES

    def _load_file(self) -> HighscoresList:
        with open(self._file_name, "r") as f:
            highscores = f.read()

        return HighscoresList.model_validate_json(highscores)
