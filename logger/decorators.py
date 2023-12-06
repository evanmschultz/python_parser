from functools import wraps
import inspect
from inspect import FrameInfo
import logging
from logging import LogRecord, Logger
from typing import Callable
import libcst


from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_stripped_code_content,
)
from utilities.processing_context import LoggingCallerInfo, NodeAndPositionData


def logging_decorator(
    level=logging.DEBUG,
    *,
    message: str | None = None,
    syntax_highlighting: bool = False,
) -> Callable:
    """
    A decorator for adding enhanced logging to functions, with optional syntax highlighting.

    This decorator logs the call to the decorated function at the specified logging level. If syntax_highlighting is enabled and the first argument of the function is a libcst.CSTNode, the decorator logs the node's content with syntax highlighting.

    Args:
        level (int): The logging level. Defaults to logging.DEBUG.
        message (str | None): Custom log message. If None, a default message is generated.
        syntax_highlighting (bool): If True, enables syntax highlighting for libcst.CSTNode arguments.

    Returns:
        Callable: The decorated function with enhanced logging capability.

    Example:
        >>> @logging_decorator(level=logging.INFO, message="Function start", syntax_highlighting=True)
        >>> def sample_function(arg1):
        >>>     pass
        # This decorates 'sample_function' with enhanced logging at INFO level.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_message: str = (
                message if message else (f"Calling function: {func.__name__}")
            )
            frame_info: inspect.FrameInfo = inspect.stack()[1]
            caller_info: LoggingCallerInfo = _get_caller_info(frame_info)
            code_content: str = _gather_code_content(syntax_highlighting, args)
            logger: Logger = _get_logger(caller_info.caller_module_name)

            _handle_logging(
                logger,
                caller_info,
                level,
                log_message,
                syntax_highlighting,
                code_content,
            )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _gather_log_record_context(
    caller_info: LoggingCallerInfo, level: int, msg: str
) -> logging.LogRecord:
    """Creates and returns a LogRecord with specified context information."""

    return logging.LogRecord(
        name=caller_info.caller_module_name,
        level=level,
        pathname=caller_info.caller_file_path,
        lineno=caller_info.caller_line_no,
        msg=msg,
        args=None,
        exc_info=None,
    )


def _get_caller_info(frame_info: FrameInfo) -> LoggingCallerInfo:
    """Extracts and returns caller information from a frame object."""

    caller_module_name: str = frame_info.filename.split("/")[-1].split(".")[0]
    caller_file_path: str = frame_info.filename
    caller_line_no: int = frame_info.lineno
    return LoggingCallerInfo(caller_module_name, caller_file_path, caller_line_no)


def _get_logger(caller_module_name: str) -> Logger:
    """Retrieves and returns a Logger instance for the specified module name."""

    return logging.getLogger(caller_module_name)


def _gather_code_content(syntax_highlighting: bool, args: tuple) -> str:
    """Gathers and returns code content for logging, if `syntax_highlighting` else returns empty string."""

    if not syntax_highlighting or not args:
        return ""

    arg_0 = args[0]
    content: str = ""

    if isinstance(arg_0, libcst.CSTNode):
        content = extract_code_content(arg_0)
    elif isinstance(arg_0, list) and all(
        isinstance(node, libcst.CSTNode) for node in arg_0
    ):
        content = "\n".join(extract_stripped_code_content(node) for node in arg_0)
    elif isinstance(arg_0, NodeAndPositionData):
        content = "\n".join(extract_stripped_code_content(node) for node in arg_0.nodes)

    return content


def _handle_syntax_highlighting(
    syntax_highlighting: bool,
    log_record: logging.LogRecord,
    logger: Logger,
    content: str,
) -> None:
    """Handles syntax highlighting for the log record if enabled."""

    if syntax_highlighting:
        log_record.syntax_highlight = syntax_highlighting
        log_record.content = content
        logger.handle(log_record)


def _handle_logging(
    logger: Logger,
    caller_info: LoggingCallerInfo,
    level: int,
    log_message: str,
    syntax_highlighting: bool,
    code_content: str,
) -> None:
    """Handles the logging process, including the creation and handling of log records."""

    if logger.isEnabledFor(level):
        log_record: LogRecord = _gather_log_record_context(
            caller_info, level, log_message
        )
        logger.handle(log_record)  # Print log message
        _handle_syntax_highlighting(
            syntax_highlighting, log_record, logger, code_content
        )
