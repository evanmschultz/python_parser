from typing import Sequence
import logging
import libcst

from logger.decorators import logging_decorator

from id_generation.id_generation_strategies import (
    StandaloneCodeBlockIDGenerationStrategy,
)

from model_builders.builder_factory import BuilderFactory
from model_builders.standalone_block_model_builder import StandaloneBlockModelBuilder
from models.enums import BlockType
from models.models import CommentModel

from visitors.node_processing.common_functions import (
    extract_important_comment,
    extract_stripped_code_content,
)
from visitors.node_processing.processing_context import NodeAndPositionData


def gather_standalone_lines(
    node_body: Sequence[libcst.CSTNode], visitor_instance
) -> list[NodeAndPositionData]:
    standalone_blocks: list[NodeAndPositionData] = []
    standalone_block: list[libcst.CSTNode] = []
    start_line = end_line = 0

    for statement in node_body:
        if _is_class_or_function_def(statement) or _is_import_statement(statement):
            if standalone_block:
                end_line = visitor_instance.get_node_position_data(
                    standalone_block[-1]
                ).end
                standalone_blocks.append(
                    NodeAndPositionData(standalone_block, start_line, end_line)
                )
                standalone_block = []
                start_line = end_line = 0
        else:
            if not standalone_block:
                start_line = visitor_instance.get_node_position_data(statement).start
            standalone_block.append(statement)

    if standalone_block:
        end_line = visitor_instance.get_node_position_data(standalone_block[-1]).end
        standalone_blocks.append(
            NodeAndPositionData(standalone_block, start_line, end_line)
        )

    return standalone_blocks


def _is_class_or_function_def(statement: libcst.CSTNode) -> bool:
    return isinstance(statement, (libcst.ClassDef, libcst.FunctionDef))


def _is_import_statement(statement: libcst.CSTNode) -> bool:
    return isinstance(statement, libcst.SimpleStatementLine) and any(
        isinstance(elem, (libcst.Import, libcst.ImportFrom)) for elem in statement.body
    )


def process_standalone_blocks(
    code_blocks: list[NodeAndPositionData], parent_id: str
) -> list[StandaloneBlockModelBuilder]:
    models: list[StandaloneBlockModelBuilder] = []
    for count, code_block in enumerate(code_blocks):
        models.append(_process_standalone_block(code_block, parent_id, count + 1))

    return models


# TODO: Fix important comment logic
@logging_decorator(level=logging.DEBUG, syntax_highlighting=True)
def _process_standalone_block(
    standalone_block: NodeAndPositionData, parent_id: str, count: int
) -> StandaloneBlockModelBuilder:
    id: str = StandaloneCodeBlockIDGenerationStrategy.generate_id(parent_id, count)
    builder: StandaloneBlockModelBuilder = BuilderFactory.create_builder_instance(
        block_type=BlockType.STANDALONE_CODE_BLOCK,
        id=id,
        parent_id=parent_id,
    )
    content, variable_assignments, important_comments = _process_nodes(standalone_block)
    (
        builder.set_start_line_num(standalone_block.start)
        .set_end_line_num(standalone_block.end)
        .set_code_content(content)
    )
    for important_comment in important_comments:
        builder.add_important_comment(important_comment)
    builder.set_variable_assignments(variable_assignments)

    return builder


def _process_nodes(
    standalone_block: NodeAndPositionData,
) -> tuple[str, list[str], list[CommentModel]]:
    content: str = ""
    variable_assignments: list[str] = []
    important_comments: list[CommentModel] = []
    for line in standalone_block.nodes:
        if isinstance(line, libcst.SimpleStatementLine):
            variable_assignments.extend(_extract_variable_assignments(line))

        important_comments.extend(_process_leading_lines(line))
        line_content: str = extract_stripped_code_content(line)
        content += line_content + "\n"

    return content, variable_assignments, important_comments


def _process_leading_lines(line: libcst.CSTNode) -> list[CommentModel]:
    important_comments: list[CommentModel] = []

    if isinstance(line, libcst.SimpleStatementLine):
        for leading_line in line.leading_lines:
            important_comment: CommentModel | None = extract_important_comment(
                leading_line
            )
            if important_comment:
                important_comments.append(important_comment)

    return important_comments


def _extract_variable_assignments(
    node: libcst.SimpleStatementLine,
) -> list[str]:
    variable_assignments: list[str] = []
    for stmt in node.body:
        if isinstance(stmt, (libcst.AnnAssign, libcst.Assign)):
            variable_assignments.append(extract_stripped_code_content(stmt))

    return variable_assignments
