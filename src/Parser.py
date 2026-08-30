from src.models import Config
from src.errors import InvalidFileSufixError
from typing import TextIO


class Parser:
    """Loads a JSON-with-comments config file into a validated Config."""

    def parse(self, config_file: str) -> Config:
        """Parse and validate a config file into a Config instance.

        Args:
            config_file: Path to the JSON config file. May contain "#" or
                "//" comments, which are stripped before parsing.

        Returns:
            A validated Config instance.

        Raises:
            InvalidFileSufixError: If config_file does not end in ".json".
            ValidationError: If the config content fails pydantic
                validation (propagated from Config construction).
            FileNotFoundError: If config_file does not exist.
        """
        if not config_file.endswith(".json"):
            raise InvalidFileSufixError(
                "InvalidFileSufixError: Config file must be '.json' "
                )
        with open(config_file, "r") as file:
            json_content = self._strip_comments(file)

        return Config.model_validate_json(json_content)

    @staticmethod
    def _strip_comments(file: TextIO) -> str:
        """Strip "#" and "//" comments from a config file's contents.

        Args:
            file: Open text file to read and strip comments from.

        Returns:
            The file's contents with every comment removed.
        """
        json_string = ""

        for line in file.readlines():
            new_line = line.split("#")[0]
            new_line = new_line.split("//")[0].strip()
            if new_line:
                json_string += new_line

        return json_string
