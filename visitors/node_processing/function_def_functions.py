from typing import Mapping, Sequence

import libcst
from libcst.metadata import CodeRange

from models.enums import BlockType
from models.models import ParameterModel

from visitors.node_processing.common_functions import extract_type_annotation
from visitors.visitor_manager import VisitorManager


def get_parameters_list(
    parameter_sequence: Sequence[libcst.Param],
) -> list[ParameterModel] | None:
    params: list[ParameterModel] | None = None

    if parameter_sequence:
        params = []
        for parameter in parameter_sequence:
            param: ParameterModel = extract_and_process_parameter(parameter)
            params.append(param)

    return params if params else None


def extract_star_parameter(param: libcst.Param) -> ParameterModel:
    star = str(param.star)
    return extract_and_process_parameter(param, star=star)


def extract_and_process_parameter(
    parameter: libcst.Param, star: str | None = None
) -> ParameterModel:
    name: str = get_parameter_name(parameter)
    annotation: str | None = extract_type_annotation(parameter)
    default: str | None = extract_default(parameter)

    parameter_content: str = construct_parameter_content(
        name=name, annotation=annotation, default=default, star=star
    )
    return ParameterModel(content=parameter_content)


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


def extract_and_process_return_annotation(
    node_returns: libcst.Annotation | None,
) -> str:
    if isinstance(node_returns, libcst.Annotation) and node_returns:
        annotation: str | None = extract_type_annotation(node_returns)
        return annotation if annotation else "No return annotation"
    else:
        return "No return annotation"


def get_function_id_context(
    function_name: str,
    parent_id: str,
) -> dict[str, str]:
    return {
        "parent_id": parent_id,
        "function_name": function_name,
    }


def get_function_position_data(
    node_name: str,
    position_metadata: Mapping[libcst.CSTNode, CodeRange],
) -> dict[str, int]:
    """Gets the start and end line numbers of a function."""
    for item in position_metadata:
        if (
            type(item) is libcst.FunctionDef or type(item) is libcst.ClassDef
        ) and item.name.value == node_name:
            start: int = position_metadata[item].start.line
            end: int = position_metadata[item].end.line

            position_data: dict[str, int] = {
                "start": start,
                "end": end,
            }
            return position_data
    raise Exception(
        "Class position data not found. Check logic in `get_and_set_class_position_data`!"
    )


def func_is_method(id: str) -> bool:
    """Returns true if an ancestor of the function is a class."""
    return str(BlockType.CLASS) in id


def func_is_async(node: libcst.FunctionDef) -> bool:
    """Returns true if the function is async."""
    return True if node.asynchronous else False


def process_function_parameters(
    node: libcst.Parameters,
) -> dict[str, ParameterModel | list[ParameterModel] | None]:
    """Processes the parameters of a function."""

    params: list[ParameterModel] | None = (
        get_parameters_list(node.params) if node.params else None
    )
    kwonly_params: list[ParameterModel] | None = (
        get_parameters_list(node.kwonly_params) if node.kwonly_params else None
    )
    posonly_params: list[ParameterModel] | None = (
        get_parameters_list(node.posonly_params) if node.posonly_params else None
    )
    star_arg: ParameterModel | None = (
        extract_star_parameter(node.star_arg)
        if node.star_arg and isinstance(node.star_arg, libcst.Param)
        else None
    )
    star_kwarg: ParameterModel | None = (
        extract_star_parameter(node.star_kwarg) if node.star_kwarg else None
    )

    return {
        "params": params,
        "kwonly_params": kwonly_params,
        "posonly_params": posonly_params,
        "star_arg": star_arg,
        "star_kwarg": star_kwarg,
    }
