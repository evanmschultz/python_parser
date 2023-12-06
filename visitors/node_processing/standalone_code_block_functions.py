from typing import Sequence
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
from utilities.processing_context import NodeAndPositionData


def gather_standalone_lines(
    node_body: Sequence[libcst.CSTNode], visitor_instance
) -> list[NodeAndPositionData]:
    """
    Gathers standalone lines of code that are not part of class or function definitions or import statements.

    This function iterates over a sequence of CSTNodes, identifying blocks of code that stand alone. Standalone blocks are those not encapsulated in class or function definitions and not part of import statements.

    Args:
        node_body: A sequence of libcst.CSTNode representing the body of a module or a block.
        visitor_instance: An instance of a visitor class that provides additional context and utilities.

    Returns:
        A list of NodeAndPositionData, each representing a standalone block of code with its start and end line numbers.

    Example:
        >>> visitor_instance = ModuleVisitor(id="module1", ...)
        >>> standalone_blocks = gather_standalone_lines(module_ast.body, visitor_instance)
        # This will process the module AST and return standalone blocks of code.
    """

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


def process_standalone_blocks(
    code_blocks: list[NodeAndPositionData], parent_id: str
) -> list[StandaloneBlockModelBuilder]:
    """
    Processes standalone blocks of code and builds models for each block.

    Iterates over a list of standalone code blocks, processing each to build a model representing the block. Each block is assigned an identifier and associated with a parent identifier.

    Args:
        code_blocks: A list of NodeAndPositionData representing standalone code blocks.
        parent_id: The identifier of the parent (usually a module or class).

    Returns:
        A list of StandaloneBlockModelBuilder, each representing a processed standalone block.

    Example:
        >>> standalone_blocks_models = process_standalone_blocks(standalone_blocks, "module1")
        # Processes standalone blocks and creates models for them.
    """

    models: list[StandaloneBlockModelBuilder] = []
    for count, code_block in enumerate(code_blocks):
        models.append(_process_standalone_block(code_block, parent_id, count + 1))

    return models


def _is_class_or_function_def(statement: libcst.CSTNode) -> bool:
    """Returns True if the statement is a class or function definition."""

    return isinstance(statement, (libcst.ClassDef, libcst.FunctionDef))


def _is_import_statement(statement: libcst.CSTNode) -> bool:
    """Returns True if the statement is an import statement."""

    return isinstance(statement, libcst.SimpleStatementLine) and any(
        isinstance(elem, (libcst.Import, libcst.ImportFrom)) for elem in statement.body
    )


# TODO: Fix important comment logic
def _process_standalone_block(
    standalone_block: NodeAndPositionData, parent_id: str, count: int
) -> StandaloneBlockModelBuilder:
    """Processes a standalone block of code and sets the attributes in the model builder, returns the builder instance."""

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


@logging_decorator(syntax_highlighting=True)
def _process_nodes(
    standalone_block: NodeAndPositionData,
) -> tuple[str, list[str], list[CommentModel]]:
    """Processes the nodes in a standalone block of code and returns the content, variable assignments and important comments."""

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
    """Processes the leading lines of a node and returns the important comments."""

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
    """Extracts variable assignments from a SimpleStatementLine node."""

    variable_assignments: list[str] = []
    for stmt in node.body:
        if isinstance(stmt, (libcst.AnnAssign, libcst.Assign)):
            variable_assignments.append(extract_stripped_code_content(stmt))

    return variable_assignments
