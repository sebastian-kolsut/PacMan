from src.MainGameLoop import MainGameLoop
from src.errors import InvalidFileSufixError
from pydantic import ValidationError
from sys import argv


def main() -> None:
    """Parse the CLI config argument and run the game.

    Expects exactly one argument: the path to a JSON config file. Any
    startup or runtime failure is caught and reported with a clean
    message instead of a raw traceback.
    """
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} <config.json>")
        return

    config_file = argv[1]

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
