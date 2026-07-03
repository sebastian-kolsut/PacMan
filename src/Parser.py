from src.models import ConfigModel
from src.errors import InvalidFileSufixError
from typing import TextIO


class Parser:

    def parse(self, config_file: str) -> ConfigModel:
        """Parse and validate a config file into a ConfigModel.

        Args:
            config_file (str): Path to the JSON config file.

        Raises:
            InvalidFileSufixError: If the file sufix is diffrent from json.
            ValidationError: If the config data fails pydantic validation
                (propagated from ConfigModel construction).
            FileNotFoundError: If the file at `path` does not exist.

        Returns:
            ConfigModel: A validated ConfigModel instance.
        """
        if not config_file.endswith(".json"):
            raise InvalidFileSufixError(
                "InvalidFileSufixError: Config file must be '.json' "
                )
        with open(config_file, "r") as file:
            json_content = self._strip_comments(file)

        return ConfigModel.model_validate_json(json_content)

    @staticmethod
    def _strip_comments(file: TextIO) -> str:
        json_string = ""

        for line in file.readlines():
            new_line = line.split("#")[0]
            new_line = new_line.split("//")[0].strip()
            if new_line:
                json_string += new_line

        return json_string
