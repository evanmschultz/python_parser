import logging
from typing import Sequence
import libcst


from models.models import CommentModel, DecoratorModel
from models.enums import CommentType


def extract_code_content(
    node: libcst.CSTNode,
) -> str:
    """
    Extracts the code content from a given CST node.

    This function converts a CST node to its string representation, maintaining the original code format.

    Args:
        node (libcst.CSTNode): The CST node to extract code from.

    Returns:
        str: The string representation of the code for the given CST node.

    Example:
        >>> extract_code_content(some_cst_node)
        # Returns the code content as a string.
    """

    return libcst.Module([]).code_for_node(node)


def extract_stripped_code_content(
    node: libcst.CSTNode,
) -> str:
    """
    Extracts the stripped code content from a given CST node.

    Similar to extract_code_content, but also strips leading and trailing whitespace from the code string.

    Args:
        node (libcst.CSTNode): The CST node to extract code from.

    Returns:
        str: The stripped string representation of the code for the CST node.

    Example:
        >>> extract_stripped_code_content(some_cst_node)
        # Returns the stripped code content as a string.
    """

    return extract_code_content(node).strip()


def extract_important_comment(
    comment_or_empty_line_node: libcst.CSTNode,
) -> CommentModel | None:
    """
    Extracts an important comment from a given CST node.

    Processes a libcst.Comment or libcst.EmptyLine node to extract important comments, categorizing them based on predefined types.

    Args:
        comment_or_empty_line_node (libcst.CSTNode): A CST node representing a comment or an empty line with a comment.

    Returns:
        CommentModel | None: A CommentModel object if an important comment is found, otherwise None.

    Example:
        >>> extract_important_comment(some_comment_node)
        # Returns a CommentModel for the comment, or None if not important.
    """

    comment_text: str | None = None

    if isinstance(comment_or_empty_line_node, libcst.EmptyLine):
        if comment_or_empty_line_node.comment:
            comment_text = comment_or_empty_line_node.comment.value
    elif isinstance(comment_or_empty_line_node, libcst.Comment):
        comment_text = comment_or_empty_line_node.value

    if not comment_text:
        return None

    comment_types: list[CommentType] = [
        comment_type
        for comment_type in CommentType
        if comment_type.value in comment_text.upper()
    ]

    if comment_types:
        return CommentModel(
            content=comment_text,
            comment_types=comment_types,
        )


def extract_decorators(
    decorators: Sequence[libcst.Decorator],
) -> list[DecoratorModel] | None:
    """
    Extracts a list of decorator models from a sequence of libcst.Decorator nodes.

    Processes each decorator node to form a model representing the decorator's name and its arguments, if any.

    Args:
        decorators (Sequence[libcst.Decorator]): A sequence of libcst.Decorator nodes.

    Returns:
        list[DecoratorModel] | None: A list of DecoratorModel objects, or None if no decorators are found.

    Example:
        >>> extract_decorators(function_node.decorators)
        # Returns a list of DecoratorModel objects representing each decorator in the function.
    """

    decorators_list: list[DecoratorModel] = []
    for decorator in decorators:
        decorator_model: DecoratorModel | None = extract_decorator(decorator)
        if isinstance(decorator_model, DecoratorModel):
            decorators_list.append(extract_decorator(decorator))  # type: ignore
    return decorators_list if decorators_list else None


def extract_decorator(
    decorator: libcst.Decorator,
) -> DecoratorModel | None:
    """
    Extracts the decorator from a libcst.Decorator node.

    Processes a single decorator node to create a model representing the decorator's name and arguments.

    Args:
        decorator (libcst.Decorator): A libcst.Decorator node.

    Returns:
        DecoratorModel | None: A DecoratorModel object if the decorator is valid, otherwise None.

    Example:
        >>> extract_decorator(some_decorator_node)
        # Returns a DecoratorModel object for the decorator.
    """

    decorator_name: str = ""
    arg_list: list[str] | None = None
    if isinstance(decorator.decorator, libcst.Name):
        decorator_name: str = decorator.decorator.value
    if isinstance(decorator.decorator, libcst.Call):
        func = decorator.decorator.func
        if isinstance(func, libcst.Name) or isinstance(func, libcst.Attribute):
            if decorator.decorator.args:
                arg_list = [
                    extract_stripped_code_content(arg)
                    for arg in decorator.decorator.args
                ]
        if isinstance(func, libcst.Name):
            decorator_name = func.value
        elif isinstance(func, libcst.Attribute):
            decorator_name = func.attr.value
        else:
            logging.warning("Decorator func is not a Name or Attribute node")

    return (
        DecoratorModel(
            content=extract_stripped_code_content(decorator),
            decorator_name=decorator_name,
            decorator_args=arg_list,
        )
        if decorator_name
        else None
    )


def extract_type_annotation(node: libcst.CSTNode) -> str | None:
    """
    Extracts the type annotation from a node.

    Processes a libcst.CSTNode to extract the type annotation, if present. It handles various forms of type annotations, including generics and unions.

    Args:
        node (libcst.CSTNode): The node to extract the type annotation from.

    Returns:
        str | None: The extracted type annotation as a string, or None if no type annotation is found.
    """

    annotation: libcst.Annotation | None = _get_node_annotation(node)
    if annotation and isinstance(annotation, libcst.Annotation):
        return _process_type_annotation_expression(annotation.annotation)
    return None


def _get_node_annotation(node: libcst.CSTNode) -> libcst.Annotation | None:
    """Retrieves the annotation of a given CSTNode."""

    if isinstance(node, libcst.Param) or isinstance(node, libcst.AnnAssign):
        return node.annotation
    elif isinstance(node, libcst.Annotation):
        return node
    return None


def _process_type_annotation_expression(expression: libcst.BaseExpression) -> str:
    """Process the type annotation expression and return a string representation recursively."""

    if isinstance(expression, libcst.Subscript):
        return _extract_generic_types_from_subscript(expression)
    elif isinstance(expression, libcst.BinaryOperation):
        left: str = _process_type_annotation_expression(expression.left)
        right: str = _process_type_annotation_expression(expression.right)
        return f"{left} | {right}"
    elif isinstance(expression, libcst.Name):
        return expression.value
    return ""


def _extract_generic_types_from_subscript(
    node: libcst.Subscript | libcst.BaseExpression,
) -> str:
    """Recursively extracts generic types from a Subscript node or a BaseExpression node."""

    if isinstance(node, libcst.Subscript):
        generics: list[str] = []
        for element in node.slice:
            if isinstance(element.slice, libcst.Index):
                if isinstance(element.slice.value, libcst.BinaryOperation):
                    union_type: str = _process_type_annotation_expression(
                        element.slice.value
                    )
                    generics.append(union_type)
                else:
                    generic_type: str = _extract_generic_types_from_subscript(
                        element.slice.value
                    )
                    generics.append(generic_type)

        if isinstance(node.value, libcst.Name):
            generics_str = ", ".join(generics)
            return f"{node.value.value}[{generics_str}]"
        else:
            return ""

    elif isinstance(node, libcst.Name):
        return node.value
    return ""
