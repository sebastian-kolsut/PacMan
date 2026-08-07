from src.screens.game.ghosts.GhostState import GhostState


def test_blinking_alternates_the_displayed_asset_every_interval() -> None:
    state = GhostState()
    state.set_frightened(True)
    state.set_blinking(True)

    assert state.show_blue_asset

    state.update(0.2)
    assert not state.show_blue_asset

    state.update(0.2)
    assert state.show_blue_asset


def test_eaten_ghost_cannot_enter_frightened_state() -> None:
    state = GhostState()
    state.eat()

    state.set_frightened(True)

    assert state.is_eaten
    assert not state.is_frightened
