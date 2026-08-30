from src.Parser import Parser
from src.models import Config
from src.errors import InvalidFileSufixError
from pydantic import ValidationError
import pytest


_VALID_FIRST_LEVELS = [
    (20, 20, 42, 90),
    (25, 25, 42, 90),
    (30, 15, 42, 90),
]


def _assert_valid_config(test_config: Config) -> None:
    assert test_config.highscore_filename == "highscores.json"
    assert test_config.lives == 3
    assert test_config.points_per_pacgum == 10
    assert test_config.points_per_super_pacgum == 50
    assert test_config.points_per_ghost == 200
    assert test_config.seed == 42
    assert len(test_config.levels) == 10

    for level, expected in zip(test_config.levels, _VALID_FIRST_LEVELS):
        width, height, pacgum, level_max_time = expected
        assert level.width == width
        assert level.height == height
        assert level.pacgum == pacgum
        assert level.level_max_time == level_max_time


def test_parsing_valid_config() -> None:
    test_config = Parser().parse("tests/jsons/valid_no_comments.json")

    _assert_valid_config(test_config)


def test_parsing_valid_with_comments() -> None:
    test_config = Parser().parse("tests/jsons/valid_with_comments.json")

    _assert_valid_config(test_config)


def test_parsing_valid_unknown_key() -> None:
    test_config = Parser().parse("tests/jsons/valid_unknown_keys.json")

    _assert_valid_config(test_config)


def test_parsing_invalid_missing_key() -> None:
    test_config = Parser().parse("tests/jsons/invalid_missing_key.json")

    assert test_config.points_per_ghost == Config().points_per_ghost


def test_parsing_invalid_pacgum_value() -> None:
    test_config = Parser().parse("tests/jsons/invalid_pacgum_value.json")

    assert test_config.levels[0].pacgum == 203
    assert len(test_config.levels) == 10


def test_parsing_invalid_highscore_file() -> None:
    test_config = Parser().parse("tests/jsons/invallid_highscore_file.json")

    assert test_config.highscore_filename == "highscores.json"


def test_parsing_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        Parser().parse("not_a_real_file.json")


def test_parsing_invalid_file_format() -> None:
    with pytest.raises(InvalidFileSufixError):
        Parser().parse("tests/jsons/invalid_file_sufix.jon")


def test_parsing_invalid_json_format() -> None:
    with pytest.raises(ValidationError):
        Parser().parse("tests/jsons/invallid_json_format.json")
