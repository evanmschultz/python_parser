from typing import Mapping, Sequence

import libcst
from libcst.metadata import CodeRange

from models.enums import BlockType

from visitors.node_processing.common_functions import extract_type_annotation
from visitors.visitor_manager import VisitorManager


def get_parameters_list(
    parameter_sequence: Sequence[libcst.Param],
) -> list[str] | None:
    parameters: list[str] = []

    for parameter in parameter_sequence:
        parameter_content: str = extract_and_process_parameter(parameter)
        parameters.append(parameter_content)

    return parameters if parameters else None


def extract_and_process_parameter(
    parameter: libcst.Param, star: str | None = None
) -> str:
    name: str = get_parameter_name(parameter)
    annotation: str | None = extract_type_annotation(parameter)
    default: str | None = extract_default(parameter)

    parameter_content: str = construct_parameter_content(
        name=name, annotation=annotation, default=default, star=star
    )
    # TODO: Add model logic, to builder
    # return ParameterModel(content=parameter_content)
    return parameter_content


def get_parameter_name(parameter: libcst.Param) -> str:
    return parameter.name.value


def extract_default(parameter: libcst.Param) -> str | None:
    """Extract the default value from a parameter."""
    return parameter.default.value if parameter.default else None  # type: ignore


def construct_parameter_content(
    name: str,
    annotation: str | None,
    default: str | None,
    star: str | None = None,
) -> str:
    content: str = name

    if star:
        content = f"{star}{name}"
    if annotation:
        content = f"{content}: {annotation}"
    if default:
        content = f"{content} = {default}"
    return content


def get_function_id(
    function_node: libcst.FunctionDef,
    parent_id: str,
    visitor_manager: VisitorManager,
) -> str:
    id_generation_context: dict[str, str] = {
        "parent_id": parent_id,
        "function_name": function_node.name.value,
    }
    function_node_id: str = visitor_manager.get_node_id(
        BlockType.FUNCTION, id_generation_context
    )
    return function_node_id


def get_function_position_data(
    node_name: str, position_metadata: Mapping[libcst.CSTNode, CodeRange]
) -> dict[str, int] | None:
    position_data: dict[str, int] | None = None

    for item in position_metadata:
        if type(item) is libcst.FunctionDef and item.name.value == node_name:
            start_line_number: int = position_metadata[item].start.line
            end_line_number: int = position_metadata[item].end.line

            position_data = {
                "start_line_number": start_line_number,
                "end_line_number": end_line_number,
            }
            break

    if position_data:
        return position_data
    else:
        raise Exception(
            "Class position data not found. Check logic in `get_and_set_class_position_data`!"
        )
