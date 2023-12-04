import logging

from rich.logging import RichHandler
from rich.syntax import Syntax


def setup_logging(level=logging.INFO) -> None:
    """
    Set up custom logging configuration with optional syntax highlighting for Python code.

    Args:
    level (logging.Level): The logging level to use.
    """
    format_str = "%(message)s"
    logging.basicConfig(level=level, format=format_str, handlers=[RichSyntaxHandler()])


class RichSyntaxHandler(RichHandler):
    def emit(self, record) -> None:
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
