from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

import libcst
from libcst.metadata import CodeRange

from model_builders.function_model_builder import FunctionModelBuilder
from models.models import DecoratorModel


@dataclass
class PositionData:
    start: int
    end: int


@dataclass
class FunctionProcessingContext:
    node_name: str
    node_id: str
    model_builder: FunctionModelBuilder
    position_metadata: Mapping[libcst.CSTNode, CodeRange]
    module_code_content: str


@dataclass
class FunctionBuilderSettingContext:
    docstring: str | None
    decorator_list: list[DecoratorModel]
    is_method: bool
    return_annotation: str
    code_content: str
    position_data: PositionData
    is_async: bool
