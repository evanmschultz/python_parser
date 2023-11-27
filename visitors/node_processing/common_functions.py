from typing import Sequence
from libcst import CSTNode, EmptyLine, Comment
import libcst
from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder
from model_builders.standalone_code_block_model_builder import (
    StandaloneCodeBlockModelBuilder,
)

from models.models import CommentModel, DecoratorModel
from models.enums import CommentType


def extract_code_content(
    module_content: str, start_line_num: int, end_line_num: int
) -> str:
    code_content_list: list[str] = module_content.split("\n")[
        start_line_num - 1 : end_line_num
    ]
    code_content: str = "\n".join(code_content_list)

    return code_content


def process_comment(
    node: libcst.CSTNode,
    model_builder: ClassModelBuilder
    | FunctionModelBuilder
    | ModuleModelBuilder
    | StandaloneCodeBlockModelBuilder,
) -> None:
    important_comment: CommentModel | None = extract_important_comment(node)
    if important_comment:
        model_builder.add_important_comment(important_comment)


def extract_important_comment(
    comment_or_empty_line_node: CSTNode,
) -> CommentModel | None:
    if (
        isinstance(comment_or_empty_line_node, EmptyLine)
        and comment_or_empty_line_node.comment
    ):
        comment_text: str | None = comment_or_empty_line_node.comment.value
    elif isinstance(comment_or_empty_line_node, Comment):
        comment_text: str | None = comment_or_empty_line_node.value
    else:
        return None

    comment_type: CommentType | None = next(
        (ct for ct in CommentType if ct.value in comment_text), None
    )
    if comment_type:
        return CommentModel(
            content=comment_text,
            comment_type=comment_type,
        )


def extract_decorators(
    decorators: Sequence[libcst.Decorator],
) -> list[DecoratorModel]:
    """Works for both class and function decorators"""

    decorator_list: list[DecoratorModel] = []

    def extract_function_name_from_decorator(
        decorator: libcst.Decorator,
    ) -> str | None:
        if isinstance(decorator.decorator, libcst.Call):
            if isinstance(decorator.decorator.func, libcst.Name):
                return decorator.decorator.func.value
        return None

    def extract_arguments_from_decorator(call: libcst.Call) -> list[str]:
        def get_value_from_arg(arg) -> str:
            return str(arg.value.value)

        return [get_value_from_arg(arg) for arg in call.args]

    def process_decorator(decorator: libcst.Decorator) -> None:
        func_name: str | None = extract_function_name_from_decorator(decorator)
        if func_name and isinstance(decorator.decorator, libcst.Call):
            args: list[str] = extract_arguments_from_decorator(decorator.decorator)
            decorator_model = DecoratorModel(
                decorator_name=func_name, decorator_args=args
            )

            decorator_list.append(decorator_model)

    def handle_non_call_decorators(decorator: libcst.Decorator) -> None:
        if isinstance(decorator.decorator, libcst.Name):
            decorator_model = DecoratorModel(decorator_name=decorator.decorator.value)
            decorator_list.append(decorator_model)

    for decorator in decorators:
        if isinstance(decorator.decorator, libcst.Call):
            process_decorator(decorator)
        else:
            handle_non_call_decorators(decorator)

    return decorator_list


def extract_type_annotation(node: libcst.CSTNode) -> str | None:
    """Extract the type annotation from a node."""

    def get_node_annotation(node: libcst.CSTNode) -> libcst.Annotation | None:
        """Get the annotation from a node."""

        if isinstance(node, libcst.Param):
            return node.annotation
        elif isinstance(node, libcst.AnnAssign):
            return node.annotation
        elif isinstance(node, libcst.Annotation):
            return node
        else:
            return None

    def process_type_annotation_expression(expression: libcst.BaseExpression) -> str:
        """Recursively process a type annotation expression."""

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
        """Recursively extract generic types from a Subscript node."""

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
