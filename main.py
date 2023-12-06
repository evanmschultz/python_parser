import logging
from logging import Logger
import typer

from logger.logging_config import setup_logging
from visitor_manager.visitor_manager import VisitorManager


def main(
    directory: str = typer.Option(
        default=".",
        prompt="Please enter a directory path",
        help="The path to the directory to parse",
    ),
    output_directory: str = typer.Option(
        default="output",
        help="The path to the output directory",
    ),
) -> None:
    """
    Parse the specified directory and save the results in the output directory.

    Args:
        directory (str): The path to the directory to parse.
        output_directory (str): The path to the output directory.

    Returns:
        None
    """

    logger: Logger = logging.getLogger(__name__)
    logger.info("Starting the directory parsing.")

    visitor_manager = VisitorManager(directory, output_directory)
    visitor_manager.process_files()
    visitor_manager.save_visited_directories()

    logger.info("Directory parsing completed.")


if __name__ == "__main__":
    setup_logging(logging.DEBUG)
    typer.run(main)
