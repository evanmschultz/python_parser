from typing import Sequence

import logging
import libcst
from id_generation.id_generation_strategies import (
    StandaloneCodeBlockIDGenerationStrategy,
)
from logger.decorators import logging_decorator
from model_builders.builder_factory import BuilderFactory
from model_builders.standalone_block_model_builder import StandaloneBlockModelBuilder
from models.enums import BlockType

from visitors.node_processing.common_functions import extract_stripped_code_content


def gather_standalone_lines(
    node_body: Sequence[libcst.CSTNode],
) -> list[list[libcst.CSTNode]]:
    standalone_blocks: list[list[libcst.CSTNode]] = []
    standalone_block: list[libcst.CSTNode] = []

    def _is_class_or_function_def(statement: libcst.CSTNode) -> bool:
        return isinstance(statement, (libcst.ClassDef, libcst.FunctionDef))

    def _is_import_statement(statement: libcst.CSTNode) -> bool:
        return isinstance(statement, libcst.SimpleStatementLine) and any(
            isinstance(elem, (libcst.Import, libcst.ImportFrom))
            for elem in statement.body
        )

    for statement in node_body:
        if _is_class_or_function_def(statement) or _is_import_statement(statement):
            if standalone_block:
                standalone_blocks.append(standalone_block)
                standalone_block = []
        else:
            standalone_block.append(statement)

    if standalone_block:
        standalone_blocks.append(standalone_block)

    return standalone_blocks


def process_standalone_blocks(
    code_blocks: list[list[libcst.CSTNode]], parent_id: str
) -> list[StandaloneBlockModelBuilder]:
    models: list[StandaloneBlockModelBuilder] = []
    for count, code_block in enumerate(code_blocks):
        models.append(_process_standalone_block(code_block, parent_id, count + 1))

    return models


@logging_decorator(level=logging.DEBUG, syntax_highlighting=True)
def _process_standalone_block(
    standalone_lines: list[libcst.CSTNode], parent_id: str, count: int
) -> StandaloneBlockModelBuilder:
    id: str = StandaloneCodeBlockIDGenerationStrategy.generate_id(parent_id, count)
    builder: StandaloneBlockModelBuilder = BuilderFactory.create_builder_instance(
        block_type=BlockType.STANDALONE_CODE_BLOCK,
        id=id,
        parent_id=parent_id,
    )
    content: str = ""
    variable_assignments: list[str] = []

    for line in standalone_lines:
        if isinstance(line, libcst.SimpleStatementLine):
            variable_assignments.extend(_extract_variable_assignments(line))
        line_content: str = extract_stripped_code_content(line)
        content += line_content + "\n"

    builder.set_code_content(content)
    builder.set_variable_assignments(variable_assignments)

    return builder


def _extract_variable_assignments(
    node: libcst.SimpleStatementLine,
) -> list[str]:
    variable_assignments: list[str] = []
    for stmt in node.body:
        if isinstance(stmt, (libcst.AnnAssign, libcst.Assign)):
            variable_assignments.append(extract_stripped_code_content(stmt))

    return variable_assignments
