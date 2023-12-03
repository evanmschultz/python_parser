from typing import Callable
import libcst

from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
    ModuleIDGenerationStrategy,
)

from models.models import CommentModel
from models.enums import BlockType, CommentType


def get_node_id(*, node_type: BlockType, context: dict[str, str]) -> str:
    """
    Generates a unique ID for a given node based on its type and context.

    Args:
        node_type (BlockType): The type of the node (e.g., MODULE, CLASS, FUNCTION).
        context (dict[str, str]): The context information used for ID generation.

    Returns:
        str: The generated unique ID for the node.

    Raises:
        ValueError: If no ID generation strategy is found for the given node type.
    """

    id_generation_strategies: dict[BlockType, Callable[..., str]] = {
        BlockType.MODULE: ModuleIDGenerationStrategy.generate_id,
        BlockType.CLASS: ClassIDGenerationStrategy.generate_id,
        BlockType.FUNCTION: FunctionIDGenerationStrategy.generate_id,
        # TODO: Add STANDALONE_CODE_BLOCK generation strategy
    }

    strategy_function = id_generation_strategies.get(node_type)
    if strategy_function:
        return strategy_function(**context)
    else:
        raise ValueError(f"No strategy found for node type: {node_type}")


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


# def extract_decorators(
#     decorators: Sequence[libcst.Decorator],
# ) -> list[DecoratorModel]:
#     """
#     Extracts decorators from a sequence of decorator nodes.

#     Args:
#         decorators (Sequence[libcst.Decorator]): The sequence of decorator nodes.

#     Returns:
#         list[DecoratorModel]: The extracted decorator models.
#     """
#     decorator_list: list[DecoratorModel] = []

#     def extract_function_name_from_decorator(
#         decorator: libcst.Decorator,
#     ) -> str | None:
#         """Extracts the function name from a decorator."""

#         if isinstance(decorator.decorator, libcst.Call):
#             if isinstance(decorator.decorator.func, libcst.Name):
#                 return decorator.decorator.func.value
#         return None

#     def extract_arguments_from_decorator(call: libcst.Call) -> list[str]:
#         """Extracts the arguments from a decorator."""

#         def get_value_from_arg(arg) -> str:
#             return str(arg.value.value)

#         return [get_value_from_arg(arg) for arg in call.args]

#     def process_decorator(decorator: libcst.Decorator) -> None:
#         """Processes a decorator and adds it to the decorator list."""
#         func_name: str | None = extract_function_name_from_decorator(decorator)
#         if func_name and isinstance(decorator.decorator, libcst.Call):
#             args: list[str] = extract_arguments_from_decorator(decorator.decorator)
#             decorator_model = DecoratorModel(
#                 decorator_name=func_name, decorator_args=args
#             )

#             decorator_list.append(decorator_model)

#     def handle_non_call_decorators(decorator: libcst.Decorator) -> None:
#         """Handles decorators that are not calls."""
#         if isinstance(decorator.decorator, libcst.Name):
#             decorator_model = DecoratorModel(decorator_name=decorator.decorator.value)
#             decorator_list.append(decorator_model)

#     for decorator in decorators:
#         if isinstance(decorator.decorator, libcst.Call):
#             process_decorator(decorator)
#         else:
#             handle_non_call_decorators(decorator)
#     return decorator_list


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
