import logging
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
    docstring: str | None = node.get_docstring()
    code_content: str = extract_code_content(node)
    bases: list[str] | None = extract_bases(node.bases)
    keywords: list[ClassKeywordModel] | None = extract_keywords(node.keywords)
    decorators: list[DecoratorModel] | None = extract_decorators(node.decorators)

    (
        builder.set_docstring(docstring)
        .set_code_content(code_content)
        .set_start_line_num(position_data.start)
        .set_end_line_num(position_data.end)
    )
    builder.set_bases(bases).set_decorators(decorators).set_keywords(keywords)


def extract_bases(bases: Sequence[libcst.Arg]) -> list[str] | None:
    bases_list: list[str] = []
    for base in bases:
        if (
            isinstance(base, libcst.Arg)
            and isinstance(base.value, libcst.Name)
            and base.value.value
        ):
            bases_list.append(base.value.value)
    return bases_list if bases_list else None


def extract_keywords(
    keywords: Sequence[libcst.Arg],
) -> list[ClassKeywordModel] | None:
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
