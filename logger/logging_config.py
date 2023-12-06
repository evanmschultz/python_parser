import logging

from rich.logging import RichHandler
from rich.syntax import Syntax


def setup_logging(level=logging.INFO) -> None:
    """
    Configures the logging system to use RichSyntaxHandler for output.

    This function sets up logging with a specific log level and format. It utilizes the RichSyntaxHandler to support rich text and syntax highlighting in log outputs.

    Args:
        level (int, optional): The logging level to set for the root logger. Defaults to logging.INFO.

    Example:
        >>> setup_logging(logging.DEBUG)
        # Configures logging at DEBUG level with RichSyntaxHandler.
    """

    format_str = "%(message)s"
    logging.basicConfig(level=level, format=format_str, handlers=[RichSyntaxHandler()])


class RichSyntaxHandler(RichHandler):
    """
    A custom logging handler that extends RichHandler to add syntax highlighting.

    This handler checks if the log record contains a 'syntax_highlight' attribute and, if so, uses 'rich.syntax.Syntax' to render the message with Python syntax highlighting.

    Inherits:
        RichHandler: The base handler provided by the rich library for rich text formatting.
    """

    def emit(self, record) -> None:
        """
        Emits a logging record.

        If the record has the 'syntax_highlight' attribute set to True, it renders the 'content' attribute of the record with syntax highlighting. Otherwise, it falls back to the standard behavior of RichHandler.

        Args:
            record: The logging record to emit.

        Example:
            # Assuming `logger` is a logger instance
            >>> logger.info("Regular log message")
            # Outputs a regular log message.

            >>> logger.info("Highlighted log message", extra={"syntax_highlight": True, "content": "print('Hello, world!')"})
            # Outputs the message with syntax highlighting.
        """

        try:
            if hasattr(record, "syntax_highlight") and getattr(
                record, "syntax_highlight"
            ):
                content: str = getattr(record, "content", "")
                if isinstance(content, str):
                    syntax = Syntax(
                        content, "python", theme="material", line_numbers=True
                    )
                    self.console.print(syntax)
                return

        except Exception as e:
            self.handleError(record)

        super().emit(record)
