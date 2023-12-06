from typing import Union

import libcst
from libcst.metadata import (
    WhitespaceInclusivePositionProvider,
    CodeRange,
)
from libcst._metadata_dependent import _UNDEFINED_DEFAULT

from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder

from models.models import (
    CommentModel,
)
from visitors.node_processing.common_functions import (
    extract_important_comment,
)
from utilities.processing_context import PositionData


BuilderType = Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder]


class BaseVisitor(libcst.CSTVisitor):
    """
    Base visitor class for traversing and processing nodes in a CST (Concrete Syntax Tree).

    This abstract class provides the foundational functionality for processing various nodes in a CST, using the libcst library. It is designed to be extended by more specific visitor classes like ModuleVisitor.

    Attributes:
        id (str): An identifier for the visitor instance.
        builder_stack (list[BuilderType]): A stack of model builders for handling different CST nodes.

    METADATA_DEPENDENCIES (tuple): Metadata dependencies required for processing the CST nodes.
    """

    METADATA_DEPENDENCIES: tuple[type[WhitespaceInclusivePositionProvider]] = (
        WhitespaceInclusivePositionProvider,
    )

    def __init__(self, id: str) -> None:
        self.id: str = id
        self.builder_stack: list[BuilderType] = []

    def visit_Comment(self, node: libcst.Comment) -> None:
        """
        Visits a Comment node in the CST.

        Extracts important comments from the node and adds them to the current builder in the stack.
        """

        parent_builder = self.builder_stack[-1]
        content: CommentModel | None = extract_important_comment(node)
        if content:
            parent_builder.add_important_comment(content)

    def get_node_position_data(
        self,
        node: libcst.CSTNode,
    ) -> PositionData:
        """
        Retrieves position data for a given CST node.

        Extracts the start and end line numbers of the node in the source code.

        Args:
            node (libcst.CSTNode): The CST node to get position data for.

        Returns:
            PositionData: An object containing start and end line numbers of the node.
        """

        position_data: CodeRange | type[_UNDEFINED_DEFAULT] = self.get_metadata(
            WhitespaceInclusivePositionProvider, node
        )

        start, end = 0, 0
        if isinstance(position_data, CodeRange):
            start: int = position_data.start.line
            end: int = position_data.end.line
        return PositionData(start=start, end=end)
