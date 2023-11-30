# TODO: method_type logic
# TODO: Fix type hinting errors

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Union
from functools import partial
import libcst
from libcst import CSTNode
from libcst.metadata import CodeRange

from model_builders.function_model_builder import FunctionModelBuilder
from models.enums import BlockType
from visitors.base_code_block_visitor import BaseCodeBlockVisitor

from models.models import (
    CommentModel,
    FunctionModel,
    ParameterListModel,
)
from visitors.node_processing.function_def_functions import (
    FunctionProcessingContext,
    get_function_id_context,
    process_function,
    process_function_parameters,
)
from visitors.node_processing.processing_context import PositionData
from visitors.visitor_manager import VisitorManager

from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_important_comment,
    extract_important_comments,
    get_node_id,
    get_node_position_data,
)

if TYPE_CHECKING:
    from visitors.class_def_visitor import ClassDefVisitor
    from visitors.module_visitor import ModuleVisitor

    from models.models import (
        ParameterModel,
    )


class FunctionDefVisitor(BaseCodeBlockVisitor):
    def __init__(
        self,
        parent_id: str,
        parent_visitor_instance: Union[
            ModuleVisitor, ClassDefVisitor, "FunctionDefVisitor"
        ],
        function_name: str,
        function_id: str,
        module_id: str,
        position_metadata: Mapping[CSTNode, CodeRange],
        module_code_content: str,
    ) -> None:
        super().__init__(
            model_builder=FunctionModelBuilder(
                parent_id=parent_id,
                function_name=function_name,
                function_id=function_id,
            ),
            parent_visitor_instance=parent_visitor_instance,
            model_id=function_id,
        )
        self.function_id: str = function_id
        self.module_id: str = module_id
        self.parent_id: str = parent_id
        self.model_builder: FunctionModelBuilder = self.model_builder
        self.visitor_manager: VisitorManager = VisitorManager.get_instance()
        self.position_metadata: Mapping[CSTNode, CodeRange] = position_metadata
        self.module_code_content: str = module_code_content
        self.node_id_generator = partial(
            get_node_id,
            node_type=BlockType.FUNCTION,
        )
        self.important_comments: list[CommentModel] = []

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        """Visits the function definition and recursively visits the children."""
        node_id_context: dict[str, str] = get_function_id_context(
            function_name=node.name.value,
            parent_id=self.model_id,
        )
        function_node_id: str = self.node_id_generator(context=node_id_context)
        print(f"\nVisiting function: {node.name.value}")

        node_position_data: PositionData = get_node_position_data(
            node.name.value, self.position_metadata
        )
        code_content: str = extract_code_content(node)

        function_processing_context: FunctionProcessingContext = (
            FunctionProcessingContext(
                node_name=node.name.value,
                node_id=self.model_id,
                model_builder=self.model_builder,
                position_data=node_position_data,
                code_content=code_content,
            )
        )
        process_function(node, function_processing_context)

        for child in node.body.body:
            if isinstance(child, libcst.FunctionDef):
                print(f"For loop: {child.name.value}")
                child_id_context: dict[str, str] = get_function_id_context(
                    function_name=child.name.value,
                    parent_id=self.model_id,
                )
                function_node_id: str = self.node_id_generator(context=child_id_context)
                child_position_data: PositionData = get_node_position_data(
                    node.name.value, self.position_metadata
                )
                child_code_content: str = extract_code_content(child)
                function_processing_context: FunctionProcessingContext = (
                    FunctionProcessingContext(
                        node_name=node.name.value,
                        node_id=self.model_id,
                        model_builder=self.model_builder,
                        position_data=child_position_data,
                        code_content=child_code_content,
                    )
                )
                has_been_processed: bool = self.visitor_manager.has_been_processed(
                    self.module_id, child_code_content
                )
                print(
                    f"Child {child.name.value} has been processed: {has_been_processed}"
                )

                if not has_been_processed:
                    print(f"Passed conditional: {child.name.value}")
                    function_visitor = FunctionDefVisitor(
                        parent_id=self.model_id,
                        parent_visitor_instance=self,
                        function_name=child.name.value,
                        function_id=function_node_id,
                        module_id=self.module_id,
                        position_metadata=self.position_metadata,
                        module_code_content=self.module_code_content,
                    )
                    child.visit(function_visitor)

    def visit_Parameters(self, node: libcst.Parameters) -> None:
        """Visits the parameters of a function definition and sets the model in the builder instance."""
        parameter_list_content: dict[
            str, ParameterModel | list[ParameterModel] | None
        ] = process_function_parameters(node)

        self.model_builder.add_parameters_list(
            ParameterListModel(
                **parameter_list_content,  # type: ignore TODO: Fix type hinting error
            )
        )

    def visit_Comment(self, node: libcst.Comment) -> None:
        """Visits the comment of a function definition and sets the model in the builder instance."""
        import_comment: CommentModel | None = extract_important_comment(node)
        if import_comment:
            self.important_comments.append(import_comment)
        print(
            f"{self.model_builder.common_attributes.id} visitor important comments: {self.important_comments}"
        )

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        """Builds the function model and adds it to the parent visitor instance."""
        self.model_builder.set_important_comments(self.important_comments)
        print(f"Function {self.model_builder.common_attributes.id} comments: ")
        for comment in self.important_comments:
            print("\t", comment)

        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: FunctionModel = self.model_builder.build()  # type: ignore
            # print(
            #     f"\n\n\n\nAdding Built Model to ModuleVisitor from FunctionDefVisitor: {built_model}\n\n\n"
            # )
            self.add_built_model_to_parent_visitor(built_model)
        # print(
        #     f"\nParent's {self.parent_visitor_instance.model_id} children printed from function visitor {self.function_id}: \n\n{self.parent_visitor_instance.children}"
        # )
