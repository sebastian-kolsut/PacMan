from src.MainGameLoop import MainGameLoop
from src.models.dataclasses import Screen

_TEST_CONFIG = "tests/jsons/valid_no_comments.json"


def test_main_menu_on_start() -> None:
    main_loop = MainGameLoop(_TEST_CONFIG)

    assert main_loop._state.screen == Screen.MAIN_MENU
