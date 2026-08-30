from enum import Enum, auto


_RESPAWN_DELAY = 5.0
_BLINK_INTERVAL = 0.20


class GhostMode(Enum):
    """The three lifecycle modes a ghost can be in."""

    NORMAL = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class GhostState:
    """Manage visual and lifecycle state for a ghost."""

    def __init__(self) -> None:
        """Initialize a ghost in its normal, non-frightened mode."""
        self._mode = GhostMode.NORMAL
        self._is_blinking = False
        self._blink_timer = 0.0
        self._show_blue_asset = False
        self._respawn_timer = 0.0

    @property
    def is_frightened(self) -> bool:
        """Whether the ghost is currently edible by Pac-Man."""
        return self._mode == GhostMode.FRIGHTENED

    @property
    def is_eaten(self) -> bool:
        """Whether the ghost has been eaten and is awaiting respawn."""
        return self._mode == GhostMode.EATEN

    @property
    def show_blue_asset(self) -> bool:
        """Whether the frightened (blue) sprite should be shown right now."""
        return self._show_blue_asset

    def update(self, delta_time: float) -> bool:
        """Advance the respawn and blink timers.

        Args:
            delta_time: Seconds elapsed since the last update.

        Returns:
            True the moment an eaten ghost finishes its respawn delay and
            returns to normal mode, False otherwise.
        """
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
        """Enter or leave frightened mode.

        Args:
            is_frightened: True to make the ghost edible, False to return
                it to normal mode. Ignored while the ghost is eaten.
        """
        if self.is_eaten:
            return

        self._mode = (
            GhostMode.FRIGHTENED if is_frightened else GhostMode.NORMAL
        )
        self._is_blinking = False
        self._blink_timer = 0.0
        self._show_blue_asset = is_frightened

    def set_blinking(self, is_blinking: bool) -> None:
        """Start or stop the frightened-mode blinking warning.

        Args:
            is_blinking: True to start alternating the sprite, False to
                stop and settle back on the frightened sprite. Ignored
                unless the ghost is currently frightened.
        """
        if self.is_eaten or not self.is_frightened:
            return

        self._is_blinking = is_blinking

        if not is_blinking:
            self._show_blue_asset = True
            self._blink_timer = 0.0

    def eat(self) -> None:
        """Mark the ghost as eaten and start its respawn countdown."""
        self._mode = GhostMode.EATEN
        self._is_blinking = False
        self._blink_timer = 0.0
        self._show_blue_asset = False
        self._respawn_timer = _RESPAWN_DELAY
