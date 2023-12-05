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
