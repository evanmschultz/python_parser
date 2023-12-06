from typing import Sequence

import libcst

from model_builders.class_model_builder import ClassModelBuilder

from models.models import ClassKeywordModel, DecoratorModel
from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_stripped_code_content,
    extract_decorators,
)
from utilities.processing_context import PositionData


def process_class_def(
    node: libcst.ClassDef,
    position_data: PositionData,
    builder: ClassModelBuilder,
) -> None:
    """
    Processes a libcst.ClassDef node to build a class model.

    Extracts various components of a class definition such as its docstring, code content, base classes, decorators, and keywords, and updates the provided ClassModelBuilder with these details.

    Args:
        node (libcst.ClassDef): The class definition node from the CST.
        position_data (PositionData): Positional data for the class in the source code.
        builder (ClassModelBuilder): The builder used to construct the class model.

    Example:
        >>> class_builder = ClassModelBuilder(id="class1", ...)
        >>> process_class_def(class_node, position_data, class_builder)
        # Processes the class definition and updates the class builder.
    """

    docstring: str | None = node.get_docstring()
    code_content: str = extract_code_content(node)
    bases: list[str] | None = _extract_bases(node.bases)
    keywords: list[ClassKeywordModel] | None = _extract_keywords(node.keywords)
    decorators: list[DecoratorModel] | None = extract_decorators(node.decorators)

    (
        builder.set_docstring(docstring)
        .set_code_content(code_content)
        .set_start_line_num(position_data.start)
        .set_end_line_num(position_data.end)
    )
    builder.set_bases(bases).set_decorators(decorators).set_keywords(keywords)


def _extract_bases(bases: Sequence[libcst.Arg]) -> list[str] | None:
    """
    Extracts the base classes from a sequence of libcst.Arg representing class bases.

    Args:
        bases (Sequence[libcst.Arg]): A sequence of libcst.Arg nodes representing class base classes.

    Returns:
        list[str] | None: A list of base class names, or None if there are no bases.

    Example:
        >>> class_bases = _extract_bases(class_node.bases)
        # Returns a list of base class names from the class definition.
    """

    bases_list: list[str] = []
    for base in bases:
        if (
            isinstance(base, libcst.Arg)
            and isinstance(base.value, libcst.Name)
            and base.value.value
        ):
            bases_list.append(base.value.value)
    return bases_list if bases_list else None


def _extract_keywords(
    keywords: Sequence[libcst.Arg],
) -> list[ClassKeywordModel] | None:
    """
    Extracts class keywords (like metaclass) from a sequence of libcst.Arg representing class keywords.

    Args:
        keywords (Sequence[libcst.Arg]): A sequence of libcst.Arg nodes representing class keywords.

    Returns:
        list[ClassKeywordModel] | None: A list of ClassKeywordModel objects representing each keyword, or None if there are no keywords.

    Example:
        >>> class_keywords = _extract_keywords(class_node.keywords)
        # Returns a list of ClassKeywordModel objects for each keyword in the class definition.
    """

    keywords_list: list[ClassKeywordModel] = []

    for keyword in keywords:
        if keyword.keyword is not None:
            keyword_name: str = keyword.keyword.value
            args: str | None = (
                extract_stripped_code_content(keyword.value) if keyword.value else None
            )
            content: str = extract_stripped_code_content(keyword)

            keyword_model = ClassKeywordModel(
                content=content, keyword_name=keyword_name, args=args
            )
            keywords_list.append(keyword_model)

    return keywords_list if keywords_list else None
