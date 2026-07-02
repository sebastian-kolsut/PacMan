from src.models import ConfigModel, LevelModel
from src.errors import InvalidFileFormatError
from typing import TextIO


class Parser:

    def parse(self, config_file: str) -> ConfigModel:
        if not config_file.endswith(".json"):
            raise InvalidFileFormatError(
                "InvalidFileFormatError: Config file must be '.json' "
                )
        with open(config_file, "r") as file:
            json_content = self.strip_comments(file)

        print(json_content)

        return ConfigModel.model_validate_json(json_content)

    @staticmethod
    def strip_comments(file: TextIO) -> str:
        json_string = ""

        for line in file.readlines():
            new_line = line.split("#")[0]
            new_line = new_line.split("//")[0].strip()
            if new_line:
                json_string += new_line

        return json_string


_VALID_CONFIG = ConfigModel(
        highscore_filename="highscores.txt",
        lives=3,
        pacgum=42,
        points_per_pacgum=10,
        points_per_super_pacgum=50,
        points_per_ghost=200,
        seed=42,
        level_max_time=90,
        level=[
            LevelModel(width=20, height=20),
            LevelModel(width=25, height=25),
            LevelModel(width=30, height=15)
        ]
        )


def test_parsing_valid_with_comments() -> None:
    test_config = Parser().parse("tests/jsons/valid_with_comments.json")

    assert test_config == _VALID_CONFIG


test_parsing_valid_with_comments()
