from functools import partial
from typing import Mapping

import libcst
from libcst import CSTNode, MetadataWrapper
from libcst.metadata import WhitespaceInclusivePositionProvider, CodeRange
from models.enums import BlockType
from models.models import CommentModel

from visitors.base_code_block_visitor import BaseCodeBlockVisitor
from model_builders.module_model_builder import ModuleModelBuilder
from visitors.class_def_visitor import ClassDefVisitor
from visitors.function_def_visitor import FunctionDefVisitor
from visitors.node_processing.class_def_functions import get_class_id_context
from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_important_comments,
    get_node_position_data,
    get_node_id,
)
from visitors.node_processing.function_def_functions import get_function_id_context
from visitors.node_processing.module_functions import (
    get_footer_content,
    get_header_content,
    process_import,
    process_import_from,
)
from visitors.node_processing.processing_context import PositionData
from visitors.visitor_manager import VisitorManager


class ModuleVisitor(BaseCodeBlockVisitor, libcst.CSTVisitor):
    """
    Visitor for processing Module nodes in the AST.

    This visitor processes each Module node and delegates processing of child nodes
    like class definitions to specific visitors.

    Args:
        file_path (str): File path of the module being visited.
        parent_visitor_instance (BaseCodeBlockVisitor): Reference to the parent visitor instance.
    """

    def __init__(
        self,
        file_path: str,
        visitor_manager: VisitorManager,
        model_id: str,
    ) -> None:
        super().__init__(
            model_builder=ModuleModelBuilder(file_path=file_path, module_id=model_id),
            model_id=model_id,
        )
        self.file_path: str = file_path
        self.model_builder: ModuleModelBuilder = self.model_builder
        self.visitor_manager: VisitorManager = visitor_manager
        self.metadata_wrapper: MetadataWrapper | None = None
        self.class_id_generator = partial(
            get_node_id,
            node_type=BlockType.CLASS,
        )
        self.function_id_generator = partial(
            get_node_id,
            node_type=BlockType.FUNCTION,
        )

    def visit_Module(self, node: libcst.Module) -> None:
        self.metadata_wrapper = MetadataWrapper(node)
        position_metadata: Mapping[CSTNode, CodeRange] = self.metadata_wrapper.resolve(
            WhitespaceInclusivePositionProvider
        )

        content: str = node.code
        docstring: str | None = node.get_docstring()
        header_content: list[str] = get_header_content(node.header)
        footer_content: list[str] = get_footer_content(node.footer)

        (
            self.model_builder.set_header_content(header_content)  # type: ignore
            .set_footer_content(footer_content)
            .set_code_content(content)
            .set_docstring(docstring)  # type: ignore
        )
        important_comments: list[CommentModel] = extract_important_comments(node)
        self.model_builder.set_important_comments(important_comments)

        for child in node.body:
            if isinstance(child, libcst.ClassDef):
                class_id_context: dict[str, str] = get_class_id_context(
                    child.name.value,
                    self.model_id,
                )
                class_node_id: str = self.class_id_generator(context=class_id_context)
                # child_class_position_data: PositionData = get_node_position_data(
                #     child.name.value, position_metadata
                # )
                class_code_content: str = extract_code_content(child)

                if not self.visitor_manager.has_been_processed(
                    self.model_id, class_code_content
                ):
                    class_name: str = child.name.value
                    class_visitor = ClassDefVisitor(
                        parent_id=self.model_id,
                        parent_visitor_instance=self,
                        class_name=class_name,
                        module_id=self.model_id,
                        class_id=class_node_id,
                        position_metadata=position_metadata,
                        module_code_content=content,
                    )
                    child.visit(class_visitor)

            if isinstance(child, libcst.FunctionDef):
                function_id_context: dict[str, str] = get_function_id_context(
                    child.name.value,
                    self.model_id,
                )
                function_node_id: str = self.function_id_generator(
                    context=function_id_context
                )

                # child_function_position_data: PositionData = get_node_position_data(
                #     child.name.value, position_metadata
                # )
                function_code_content: str = extract_code_content(child)

                if not self.visitor_manager.has_been_processed(
                    self.model_id, function_code_content
                ):
                    function_name: str = child.name.value
                    class_visitor = FunctionDefVisitor(
                        parent_id=self.model_id,
                        parent_visitor_instance=self,
                        function_name=function_name,
                        function_id=function_node_id,
                        module_id=self.model_id,
                        position_metadata=position_metadata,
                        module_code_content=content,
                    )
                    child.visit(class_visitor)

    def visit_Import(self, node: libcst.Import) -> None:
        process_import(node, self.model_builder)

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        process_import_from(node, self.model_builder)

    # def visit_Comment(self, node: libcst.Comment) -> None:
    #     process_comment(node, self.model_builder)

    def leave_Module(self, original_node: libcst.Module) -> None:
        # print(f"\nModule children printed from module visitor: {self.children}\n")
        for child in self.children:
            if child.block_type == BlockType.FUNCTION:
                ...
                # print(
                #     f"\nAdding function {child.function_name} to module {child.block_start_line_number}\n"
                # )
            self.model_builder.add_child(child)
