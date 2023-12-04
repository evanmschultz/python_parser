import logging
from typing import Sequence
import libcst


from models.models import CommentModel, DecoratorModel
from models.enums import CommentType


def extract_code_content(
    node: libcst.CSTNode,
) -> str:
    return libcst.Module([]).code_for_node(node)


def extract_stripped_code_content(
    node: libcst.CSTNode,
) -> str:
    return extract_code_content(node).strip()


def extract_important_comment(
    comment_or_empty_line_node: libcst.CSTNode,
) -> CommentModel | None:
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
        if comment_type.value in comment_text
    ]

    if comment_types:
        return CommentModel(
            content=comment_text,
            comment_types=comment_types,
        )


def extract_decorators(
    decorators: Sequence[libcst.Decorator],
) -> list[DecoratorModel] | None:
    decorators_list: list[DecoratorModel] = []
    for decorator in decorators:
        decorator_model: DecoratorModel | None = extract_decorator(decorator)
        if isinstance(decorator_model, DecoratorModel):
            decorators_list.append(extract_decorator(decorator))  # type: ignore
    return decorators_list if decorators_list else None


def extract_decorator(
    decorator: libcst.Decorator,
) -> DecoratorModel | None:
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

    Args:
        node (libcst.CSTNode): The node to extract the type annotation from.

    Returns:
        str | None: The extracted type annotation, or None if no type annotation is found.
    """

    def get_node_annotation(node: libcst.CSTNode) -> libcst.Annotation | None:
        """Retrieves the annotation of a given CSTNode."""
        if isinstance(node, libcst.Param) or isinstance(node, libcst.AnnAssign):
            return node.annotation
        elif isinstance(node, libcst.Annotation):
            return node
        return None

    def process_type_annotation_expression(expression: libcst.BaseExpression) -> str:
        """Process the type annotation expression and return a string representation recursively."""
        if isinstance(expression, libcst.Subscript):
            return extract_generic_types_from_subscript(expression)
        elif isinstance(expression, libcst.BinaryOperation):
            left: str = process_type_annotation_expression(expression.left)
            right: str = process_type_annotation_expression(expression.right)
            return f"{left} | {right}"
        elif isinstance(expression, libcst.Name):
            return expression.value
        return ""

    def extract_generic_types_from_subscript(
        node: libcst.Subscript | libcst.BaseExpression,
    ) -> str:
        """Recursively extracts generic types from a Subscript node or a BaseExpression node."""
        if isinstance(node, libcst.Subscript):
            generics: list[str] = []
            for element in node.slice:
                if isinstance(element.slice, libcst.Index):
                    if isinstance(element.slice.value, libcst.BinaryOperation):
                        union_type: str = process_type_annotation_expression(
                            element.slice.value
                        )
                        generics.append(union_type)
                    else:
                        generic_type: str = extract_generic_types_from_subscript(
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

    annotation: libcst.Annotation | None = get_node_annotation(node)
    if annotation and isinstance(annotation, libcst.Annotation):
        return process_type_annotation_expression(annotation.annotation)
    return None
