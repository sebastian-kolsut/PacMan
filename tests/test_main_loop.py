from src.MainGameLoop import MainGameLoop
from src.dataclasses import Screen


def test_main_menu_on_start() -> None:
    main_loop = MainGameLoop()

    assert main_loop._state.screen == Screen.MAIN_MENU
