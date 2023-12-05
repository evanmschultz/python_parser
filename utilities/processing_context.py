from dataclasses import dataclass

import libcst


@dataclass
class PositionData:
    start: int
    end: int


@dataclass
class NodeAndPositionData:
    nodes: list[libcst.CSTNode]
    start: int
    end: int


@dataclass
class LoggingCallerInfo:
    caller_module_name: str
    caller_file_path: str
    caller_line_no: int
