from functools import wraps
import inspect
import logging
from logging import Logger
import libcst


from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_stripped_code_content,
)


def logging_decorator(
    level=logging.INFO,
    *,
    message: str | None = None,
    syntax_highlighting: bool = False,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the current call stack, so you can find out the caller of the wrapper
            frame_info = inspect.stack()[1]
            caller_module = inspect.getmodule(frame_info.frame)
            caller_module_name = caller_module.__name__ if caller_module else "Unknown"
            caller_line_no = frame_info.lineno
            caller_file_path = frame_info.filename

            log_message: str = (
                message if message else (f"Calling function: {func.__name__}")
            )

            logger: Logger = logging.getLogger(caller_module_name)

            content = ""
            if syntax_highlighting:
                if isinstance(args[0], libcst.CSTNode):
                    content = extract_code_content(args[0])
                elif isinstance(args[0], list) and all(
                    isinstance(node, libcst.CSTNode) for node in args[0]
                ):
                    content = "\n".join(
                        extract_stripped_code_content(node) for node in args[0]
                    )

            if logger.isEnabledFor(level):
                log_record = logging.LogRecord(
                    name=caller_module_name,
                    level=level,
                    pathname=caller_file_path,
                    lineno=caller_line_no,
                    msg=log_message,
                    args=None,
                    exc_info=None,
                )
                logger.handle(log_record)  # Print log message

                if syntax_highlighting:  # Add syntax highlighted code after log message
                    log_record.syntax_highlight = syntax_highlighting
                    log_record.content = content
                    logger.handle(log_record)

            return func(*args, **kwargs)

        return wrapper

    return decorator
