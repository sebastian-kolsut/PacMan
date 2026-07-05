from src.Parser import Parser
from src.models import Config, LevelModel
from src.errors import InvalidFileSufixError
from pydantic import ValidationError
import pytest

_VALID_CONFIG = Config(
        highscore_filename="highscores.txt",
        lives=3,
        pacgum=42,
        points_per_pacgum=10,
        points_per_super_pacgum=50,
        points_per_ghost=200,
        seed=42,
        level_max_time=90,
        levels=[
            LevelModel(width=20, height=20),
            LevelModel(width=25, height=25),
            LevelModel(width=30, height=15)
        ]
        )

_VALID_CONFIG_DEFAULT = Config(pacgum=42)


def test_parsing_valid_config() -> None:
    test_config = Parser().parse("tests/jsons/valid_no_comments.json")

    assert test_config == _VALID_CONFIG


def test_parsing_valid_with_comments() -> None:
    test_config = Parser().parse("tests/jsons/valid_with_comments.json")

    assert test_config == _VALID_CONFIG


def test_parsing_valid_unknown_key() -> None:
    test_config = Parser().parse("tests/jsons/valid_unknown_keys.json")

    assert test_config == _VALID_CONFIG


def test_parsing_invalid_missing_key() -> None:
    test_config = Parser().parse("tests/jsons/invalid_missing_key.json")

    assert \
        test_config.points_per_ghost == _VALID_CONFIG_DEFAULT.points_per_ghost


def test_parsing_invalid_pacgum_value() -> None:
    test_config = Parser().parse("tests/jsons/invalid_pacgum_value.json")

    assert test_config.pacgum == 100


def test_parsing_invalid_highscore_file() -> None:
    test_config = Parser().parse("tests/jsons/invallid_highscore_file.json")

    assert test_config.highscore_filename == "highscores.txt"


def test_parsing_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        Parser().parse("not_a_real_file.json")


def test_parsing_invalid_file_format() -> None:
    with pytest.raises(InvalidFileSufixError):
        Parser().parse("tests/jsons/invalid_file_sufix.jon")


def test_parsing_invalid_json_format() -> None:
    with pytest.raises(ValidationError):
        Parser().parse("tests/jsons/invallid_json_format.json")
