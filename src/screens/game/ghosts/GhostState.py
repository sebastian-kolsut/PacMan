from enum import Enum, auto


_RESPAWN_DELAY = 5.0
_BLINK_INTERVAL = 0.20


class GhostMode(Enum):
    NORMAL = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class GhostState:
    """Manage visual and lifecycle state for a ghost."""

    def __init__(self) -> None:
        self._mode = GhostMode.NORMAL
        self._is_blinking = False
        self._blink_timer = 0.0
        self._show_blue_asset = False
        self._respawn_timer = 0.0

    @property
    def is_frightened(self) -> bool:
        return self._mode == GhostMode.FRIGHTENED

    @property
    def is_eaten(self) -> bool:
        return self._mode == GhostMode.EATEN

    @property
    def show_blue_asset(self) -> bool:
        return self._show_blue_asset

    def update(self, delta_time: float) -> bool:
        """Update timers and return whether an eaten ghost must respawn."""
        if self.is_eaten:
            self._respawn_timer -= delta_time

            if self._respawn_timer <= 0:
                self._mode = GhostMode.NORMAL
                self._respawn_timer = 0.0
                return True

            return False

        if self._is_blinking:
            self._blink_timer -= delta_time

            if self._blink_timer <= 0:
                self._blink_timer = _BLINK_INTERVAL
                self._show_blue_asset = not self._show_blue_asset

        return False

    def set_frightened(self, is_frightened: bool) -> None:
        if self.is_eaten:
            return

        self._mode = (
            GhostMode.FRIGHTENED if is_frightened else GhostMode.NORMAL
        )
        self._is_blinking = False
        self._blink_timer = 0.0
        self._show_blue_asset = is_frightened

    def set_blinking(self, is_blinking: bool) -> None:
        if self.is_eaten or not self.is_frightened:
            return

        self._is_blinking = is_blinking

        if not is_blinking:
            self._show_blue_asset = True
            self._blink_timer = 0.0

    def eat(self) -> None:
        self._mode = GhostMode.EATEN
        self._is_blinking = False
        self._blink_timer = 0.0
        self._show_blue_asset = False
        self._respawn_timer = _RESPAWN_DELAY
