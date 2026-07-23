from src.Highscores import Highscores, HighscoreData


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

    assert highscores._highscores.root[0] == HighscoreData(name="HHH", score=1000)


def test_highest_score_is_first_when_added_score_is_lowest() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("III", 1)

    assert highscores._highscores.root[0].score == 300


def test_highest_score_stays_first_at_top_of_file() -> None:
    highscores = Highscores(_TEST_FILE)

    highscores.add_score("JJJ", 150)
    highscores.add_score("KKK", 500)
    highscores.add_score("LLL", 50)

    assert highscores._highscores.root[0] == HighscoreData(name="KKK", score=500)


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
