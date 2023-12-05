from typing import Sequence

import libcst

from model_builders.function_model_builder import FunctionModelBuilder

from models.enums import BlockType
from models.models import DecoratorModel, ParameterListModel, ParameterModel
from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_decorators,
    extract_stripped_code_content,
    extract_type_annotation,
)

from utilities.processing_context import PositionData


def process_func_def(
    func_id: str,
    node: libcst.FunctionDef,
    position_data: PositionData,
    func_builder: FunctionModelBuilder,
) -> None:
    docstring: str | None = node.get_docstring()
    code_content: str = extract_code_content(node)
    decorators: list[DecoratorModel] | None = extract_decorators(node.decorators)

    returns: str = (
        extract_return_annotation(node.returns)
        if node.returns
        else "Function has no return annotation"
    )

    (
        func_builder.set_docstring(docstring)
        .set_code_content(code_content)
        .set_start_line_num(position_data.start)
        .set_end_line_num(position_data.end)
        .set_decorators(decorators)  # type: ignore
        .set_is_method(func_is_method(func_id))  # type: ignore
        .set_is_async(func_is_async(node))
        .set_return_annotation(returns)
    )


def func_is_method(id: str) -> bool:
    """Returns true if an ancestor of the function is a class."""
    return str(BlockType.CLASS) in id


def func_is_async(node: libcst.FunctionDef) -> bool:
    """Returns true if the function is async."""
    return True if node.asynchronous else False


def get_parameters_list(
    parameter_sequence: Sequence[libcst.Param],
) -> list[ParameterModel] | None:
    params: list[ParameterModel] | None = None

    if parameter_sequence:
        params = []
        for parameter in parameter_sequence:
            param: ParameterModel = ParameterModel(
                content=extract_stripped_code_content(parameter)
            )
            params.append(param)

    return params if params else None


def process_parameters(
    node: libcst.Parameters,
) -> ParameterListModel | None:
    params: list[ParameterModel] | None = (
        get_parameters_list(node.params) if node.params else []
    )
    kwonly_params: list[ParameterModel] | None = (
        get_parameters_list(node.kwonly_params) if node.kwonly_params else []
    )
    posonly_params: list[ParameterModel] | None = (
        get_parameters_list(node.posonly_params) if node.posonly_params else []
    )

    star_arg: ParameterModel | None = (
        ParameterModel(content=extract_stripped_code_content(node.star_arg))
        if node.star_arg and isinstance(node.star_arg, libcst.Param)
        else None
    )
    star_kwarg: ParameterModel | None = (
        ParameterModel(content=extract_stripped_code_content(node.star_kwarg))
        if node.star_kwarg
        else None
    )

    if params and kwonly_params and posonly_params and star_arg and star_kwarg:
        return ParameterListModel(
            params=params,
            kwonly_params=kwonly_params,
            posonly_params=posonly_params,
            star_arg=star_arg,
            star_kwarg=star_kwarg,
        )
    else:
        return None


def extract_return_annotation(
    node_returns: libcst.Annotation | None,
) -> str:
    if isinstance(node_returns, libcst.Annotation) and node_returns:
        annotation: str | None = extract_type_annotation(node_returns)
        return annotation if annotation else "No return annotation"
    else:
        return "No return annotation"
