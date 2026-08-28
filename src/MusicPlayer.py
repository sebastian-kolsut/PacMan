import pygame
from src.models.dataclasses import ProgramState, Screen

_VOLUME_STEPS = 10

_MENU_TRACK = "assets/music/Pac-Man_main_menu.mp3"
_GAME_TRACKS = [
    "assets/music/Pac-Man_game_1.mp3",
    "assets/music/Pac-Man_game_2.mp3",
]
_SCREEN_TRACKS = {
    Screen.MAIN_MENU: _MENU_TRACK,
    Screen.INSTRUCTIONS: _MENU_TRACK,
    Screen.HIGHSCORES: _MENU_TRACK,
    Screen.WIN_OR_LOSE: _MENU_TRACK,
}


class MusicPlayer:
    def __init__(self, program_state: ProgramState) -> None:
        self._program_state = program_state
        self._current_track: str | None = None
        self._last_volume: int | None = None
        self._audio_available = True

        try:
            pygame.mixer.init()
        except (pygame.error, NotImplementedError) as exc:
            print(f"Warning: audio unavailable, music disabled ({exc})")
            self._audio_available = False

    def update(self) -> None:
        if not self._audio_available:
            return

        self._sync_volume()

        track = self._get_desired_track()
        if track is not None and track != self._current_track:
            self._current_track = track
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(loops=-1)

    def _get_desired_track(self) -> str | None:
        screen = self._program_state.screen

        if screen == Screen.GAME_PLAYING:
            return _GAME_TRACKS[self._program_state.level % 2]
        if screen == Screen.SETTINGS:
            return None

        return _SCREEN_TRACKS.get(screen, _MENU_TRACK)

    def _sync_volume(self) -> None:
        if self._program_state.music_volume == self._last_volume:
            return

        self._last_volume = self._program_state.music_volume
        pygame.mixer.music.set_volume(self._last_volume / _VOLUME_STEPS)
