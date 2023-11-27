from typing import Mapping, Sequence
import libcst
from libcst.metadata import CodeRange
from model_builders.class_model_builder import ClassModelBuilder

from models.enums import BlockType
from models.models import ClassKeywordModel
from visitors.visitor_manager import VisitorManager


def get_class_id(
    class_node: libcst.ClassDef, parent_id: str, visitor_manager: VisitorManager
) -> str:
    """
    Get the unique identifier for a class node.

    Args:
        child (libcst.ClassDef): The class node.
        parent_id (str): The identifier of the parent node.
        visitor_manager (VisitorManager): The visitor manager.

    Returns:
        str: The unique identifier for the class node.
    """
    id_generation_context: dict[str, str] = {
        "parent_id": parent_id,
        "class_name": class_node.name.value,
    }
    class_node_id: str = visitor_manager.get_node_id(
        BlockType.CLASS, id_generation_context
    )
    return class_node_id


def get_class_position_data(
    node_name: str, position_metadata: Mapping[libcst.CSTNode, CodeRange]
) -> dict[str, int] | None:
    position_data: dict[str, int] | None = None

    for item in position_metadata:
        if type(item) is libcst.ClassDef and item.name.value == node_name:
            start_line_number: int = position_metadata[item].start.line
            end_line_number: int = position_metadata[item].end.line

            position_data = {
                "start_line_number": start_line_number,
                "end_line_number": end_line_number,
            }

    if position_data:
        return position_data
    else:
        raise Exception(
            "Class position data not found. Check logic in `get_and_set_class_position_data`!"
        )


def get_and_set_class_bases(
    bases: Sequence[libcst.Arg], model_builder: ClassModelBuilder
) -> None:
    for base in bases:
        if isinstance(base, libcst.Arg):
            arg_value: str | None = None
            if isinstance(base.value, libcst.Name):
                arg_value = base.value.value

            if arg_value:
                model_builder.add_base_class(arg_value)


def get_and_set_class_keywords(
    keywords: Sequence[libcst.Arg], model_builder: ClassModelBuilder
) -> None:
    for keyword_arg in keywords:
        if isinstance(keyword_arg, libcst.Arg):
            keyword: str | None = (
                keyword_arg.keyword.value if keyword_arg.keyword else None
            )

            if isinstance(keyword_arg.value, libcst.Name):
                arg_value: str = keyword_arg.value.value
            elif isinstance(keyword_arg.value, libcst.Integer):
                arg_value = str(keyword_arg.value.value)
            else:
                arg_value = str(keyword_arg.value)

            if keyword and arg_value:
                model_builder.add_keyword(
                    ClassKeywordModel(keyword_name=keyword, arg_value=arg_value)
                )
            else:
                raise Exception(
                    "Keyword or argument value not found for class keyword. Check logic in `get_and_set_class_keywords`!"
                )
