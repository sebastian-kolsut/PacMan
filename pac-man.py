from src.MainGameLoop import MainGameLoop
from src.errors import InvalidFileSufixError
from pydantic import ValidationError
from sys import argv
import os
import sys


def _chdir_to_app_dir() -> None:
    """Make the working directory match the game's own location.

    Every asset/font path in the codebase is written relative to the
    project root (e.g. "assets/menu/..."), which only resolves
    correctly if the process's current working directory is wherever
    pac-man.py (or the packaged executable) actually lives - not
    wherever the game happened to be launched from.
    """
    if getattr(sys, "frozen", False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(app_dir)


def main() -> None:
    """Parse the CLI config argument and run the game.

    Expects exactly one argument: the path to a JSON config file. Any
    startup or runtime failure is caught and reported with a clean
    message instead of a raw traceback.
    """
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} <config.json>")
        return

    # Resolve the config path before changing directories, so a
    # relative path typed relative to the caller's own shell still
    # works after _chdir_to_app_dir() moves the working directory.
    config_file = os.path.abspath(argv[1])
    _chdir_to_app_dir()

    try:
        main_loop = MainGameLoop(config_file)
    except (InvalidFileSufixError, ValidationError, FileNotFoundError):
        print("Invalid config file or file name.")
        return

    try:
        main_loop.run()
    except Exception as error:
        print(f"The game crashed unexpectedly: {error}")


if __name__ == "__main__":
    main()
