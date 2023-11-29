from typing import Sequence

import libcst

from model_builders.function_model_builder import FunctionModelBuilder

from models.enums import BlockType
from models.models import DecoratorModel, ParameterModel

from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_decorators,
    extract_type_annotation,
    get_node_position_data,
)
from visitors.node_processing.processing_context import (
    FunctionBuilderSettingContext,
    FunctionProcessingContext,
    PositionData,
)


def process_function(
    node: libcst.FunctionDef, context: FunctionProcessingContext
) -> None:
    """
    Processes a function node and sets the corresponding data in the model builder.

    Args:
        node (libcst.FunctionDef): The function node to process.
        context (FunctionProcessingContext): The context for function processing.

    Returns:
        None
    """
    position_data: PositionData = get_node_position_data(
        context.node_name, context.position_metadata
    )
    code_content: str = extract_code_content(
        context.module_code_content,
        position_data.start,
        position_data.end,
    )
    decorator_list: list[DecoratorModel] = extract_decorators(node.decorators)
    docstring: str | None = node.get_docstring()
    return_annotation: str = extract_and_process_return_annotation(node.returns)
    is_method: bool = func_is_method(context.node_id)
    is_async: bool = func_is_async(node)

    set_function_data_in_builder(
        model_builder=context.model_builder,
        context=FunctionBuilderSettingContext(
            docstring=docstring,
            decorator_list=decorator_list,
            is_method=is_method,
            return_annotation=return_annotation,
            code_content=code_content,
            position_data=position_data,
            is_async=is_async,
        ),
    )


def set_function_data_in_builder(
    model_builder: FunctionModelBuilder, context: FunctionBuilderSettingContext
) -> None:
    """Sets the function data in the builder instance."""
    (
        model_builder.set_docstring(context.docstring)
        .set_decorator_list(context.decorator_list)
        .set_is_method(context.is_method)
        .set_return_annotation(context.return_annotation)
        .set_code_content(context.code_content)
        .set_block_start_line_number(context.position_data.start)
        .set_block_end_line_number(context.position_data.end)
        .set_is_async(context.is_async)  # type: ignore TODO: Fix type hinting error
    )


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
