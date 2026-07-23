from pydantic import BaseModel, RootModel
from typing import List


_MAX_ENTRIES = 10


class HighscoreData(BaseModel):
    name: str
    score: int


class HighscoresList(RootModel):
    root: List[HighscoreData]


class Highscores:
    def __init__(self, file_name: str):
        self._file_name = file_name
        self._highscores = self._load_file()

    def add_score(self, name: str, score: int) -> None:
        self._highscores.root.append(HighscoreData(name=name, score=score))
        self._highscores.root.sort(key=lambda x: x.score, reverse=True)
        del self._highscores.root[_MAX_ENTRIES:]

    def _load_file(self) -> HighscoresList:
        with open(self._file_name, "r") as f:
            highscores = f.read()

        return HighscoresList.model_validate_json(highscores)
