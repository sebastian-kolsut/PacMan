from pathlib import Path

import pytest

from src.Highscores import (
    Highscores,
    HighscoreData,
    NameToLongError,
    NegativeScoreError,
    NotAlphanumericError,
)


_TEST_FILE = "tests/jsons/highscores_test.json"


def test_add_score_appends_entry() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("DDD", 50)

    assert HighscoreData(name="DDD", score=50) in highscores._highscores.root


def test_add_score_increases_length() -> None:
    highscores = Highscores(_TEST_FILE)
    initial_length = len(highscores._highscores.root)

    highscores.add_score("EEE", 400)
    for score in highscores._highscores.root:
        print(score.name, score.score)

    assert len(highscores._highscores.root) == initial_length + 1


def test_add_score_sorts_by_score_ascending() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("FFF", 1)

    scores = [entry.score for entry in highscores._highscores.root]
    assert scores == sorted(scores, reverse=True)


def test_add_score_inserts_at_correct_index() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("GGG", 250)

    names = [entry.name for entry in highscores._highscores.root]
    assert names.index("GGG") == 1


def test_highest_score_is_first_when_added_score_is_highest() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("HHH", 1000)

    assert highscores._highscores.root[0] == \
        HighscoreData(name="HHH", score=1000)


def test_highest_score_is_first_when_added_score_is_lowest() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("III", 1)

    assert highscores._highscores.root[0].score == 300


def test_highest_score_stays_first_at_top_of_file() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("JJJ", 150)
    highscores.add_score("KKK", 500)
    highscores.add_score("LLL", 50)

    assert highscores._highscores.root[0] == \
        HighscoreData(name="KKK", score=500)


def test_add_score_truncates_to_ten_entries() -> None:
    highscores = Highscores(_TEST_FILE)

    for i in range(10):
        highscores.add_score(f"P{i}", i)

    assert len(highscores._highscores.root) == 10


def test_add_score_truncation_drops_lowest_scores() -> None:
    highscores = Highscores(_TEST_FILE)

    for i in range(10):
        highscores.add_score(f"P{i}", i)

    scores = [entry.score for entry in highscores._highscores.root]
    assert min(scores) > 0


def test_write_scores_writes_current_scores_to_file(tmp_path: Path) -> None:
    file_path = tmp_path / "highscores.json"
    file_path.write_text(Path(_TEST_FILE).read_text())
    highscores = Highscores(str(file_path))

    highscores.add_score("ZZZ", 999)
    highscores.write_scores()

    reloaded = Highscores(str(file_path))
    assert reloaded._highscores.root == highscores._highscores.root
    assert HighscoreData(name="ZZZ", score=999) in reloaded._highscores.root


def test_missing_file_creates_new_empty_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.json"
    assert not file_path.exists()

    highscores = Highscores(str(file_path))

    assert file_path.exists()
    assert highscores._highscores.root == []


def test_invalid_format_creates_new_empty_file(tmp_path: Path) -> None:
    file_path = tmp_path / "invalid.json"
    file_path.write_text("this is not valid json")

    highscores = Highscores(str(file_path))

    assert highscores._highscores.root == []

    reloaded = Highscores(str(file_path))
    assert reloaded._highscores.root == []


def test_add_score_accepts_alphanumeric_name() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("ABC123", 10)

    assert HighscoreData(name="ABC123", score=10) in \
        highscores._highscores.root


def test_add_score_accepts_name_with_spaces() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("AB CD", 10)

    assert HighscoreData(name="AB CD", score=10) in highscores._highscores.root


def test_add_score_accepts_name_exactly_max_length() -> None:
    highscores = Highscores(_TEST_FILE)
    name = "A" * 10

    highscores.add_score(name, 10)

    assert HighscoreData(name=name, score=10) in highscores._highscores.root


def test_add_score_raises_name_too_long_error() -> None:
    highscores = Highscores(_TEST_FILE)
    name = "A" * 11

    with pytest.raises(NameToLongError):
        highscores.add_score(name, 10)


def test_add_score_raises_not_alphanumeric_error_for_special_characters() \
        -> None:
    highscores = Highscores(_TEST_FILE)

    with pytest.raises(NotAlphanumericError):
        highscores.add_score("AB-CD", 10)


def test_add_score_raises_not_alphanumeric_error_for_empty_name() -> None:
    highscores = Highscores(_TEST_FILE)

    with pytest.raises(NotAlphanumericError):
        highscores.add_score("", 10)


def test_add_score_rejected_name_does_not_change_length() -> None:
    highscores = Highscores(_TEST_FILE)
    initial_length = len(highscores._highscores.root)

    with pytest.raises(NameToLongError):
        highscores.add_score("A" * 11, 10)

    assert len(highscores._highscores.root) == initial_length


def test_add_score_raises_negative_score_error() -> None:
    highscores = Highscores(_TEST_FILE)

    with pytest.raises(NegativeScoreError):
        highscores.add_score("MMM", -1)


def test_add_score_rejected_negative_score_does_not_change_length() -> None:
    highscores = Highscores(_TEST_FILE)
    initial_length = len(highscores._highscores.root)

    with pytest.raises(NegativeScoreError):
        highscores.add_score("MMM", -1)

    assert len(highscores._highscores.root) == initial_length
