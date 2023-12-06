from dataclasses import dataclass

import libcst


@dataclass
class PositionData:
    """Positional data for a node in the syntax tree."""

    start: int
    end: int


@dataclass
class NodeAndPositionData:
    """A node in the syntax tree and its positional data."""

    nodes: list[libcst.CSTNode]
    start: int
    end: int


@dataclass
class LoggingCallerInfo:
    """Information about the caller of a function that is being logged. Used for `logging_decorator`."""

    caller_module_name: str
    caller_file_path: str
    caller_line_no: int
