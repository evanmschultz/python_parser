import logging
from logging import Logger

from models.models import ModuleModel
from parsers.python_parser import PythonParser

from rich.logging import RichHandler
import typer


def main() -> None:
    """
    Main function that parses a Python file and saves the parsed data to a JSON file.

    Returns:
        None
    """
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", handlers=[RichHandler()]
    )

    logger: Logger = logging.getLogger(__name__)

    parser = PythonParser("./sample_file.py")
    code: str = parser.open_file()
    module_model: ModuleModel | None = parser.parse(code)

    if isinstance(module_model, ModuleModel):
        parsed_data_json: str = module_model.model_dump_json(indent=4)
        json_file_name: str = "Output.json"

        with open(json_file_name, "w") as outfile:
            outfile.write(parsed_data_json)

        logger.info(f"Parsed data saved to: {json_file_name}")
    else:
        logger.error("Error: The parsed model is not of the expected type.")


if __name__ == "__main__":
    typer.run(main)
