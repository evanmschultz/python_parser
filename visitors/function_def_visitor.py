from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Sequence, Union
import libcst
from libcst import CSTNode
from libcst.metadata import CodeRange

from model_builders.function_model_builder import FunctionModelBuilder
from visitors.base_code_block_visitor import BaseCodeBlockVisitor

from models.models import (
    FunctionModel,
    DecoratorModel,
)
from visitors.node_processing.function_def_functions import (
    extract_and_process_parameter,
    get_function_id,
    get_function_position_data,
    get_parameters_list,
)
from visitors.visitor_manager import VisitorManager

from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_decorators,
    process_comment,
)

if TYPE_CHECKING:
    from visitors.class_def_visitor import ClassDefVisitor
    from visitors.module_visitor import ModuleVisitor


class FunctionDefVisitor(BaseCodeBlockVisitor):
    def __init__(
        self,
        parent_id: str,
        parent_visitor_instance: Union[
            ModuleVisitor, "ClassDefVisitor", "FunctionDefVisitor"
        ],
        function_name: str,
        function_id: str,
        position_metadata: Mapping[CSTNode, CodeRange],
        module_code_content: str,
    ) -> None:
        super().__init__(
            model_builder=FunctionModelBuilder(
                parent_id=parent_id,
                function_name=function_name,
                function_id=function_id,
            ),
            file_path=parent_visitor_instance.file_path,
            parent_visitor_instance=parent_visitor_instance,
            model_id=function_id,
        )
        self.parent_id: str = parent_id
        self.model_builder: FunctionModelBuilder = self.model_builder
        self.visitor_manager: VisitorManager = VisitorManager.get_instance()
        self.position_metadata: Mapping[CSTNode, CodeRange] = position_metadata
        self.module_code_content: str = module_code_content

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        function_node_id: str = get_function_id(
            function_node=node,
            parent_id=self.model_id,
            visitor_manager=self.visitor_manager,
        )

        if not self.visitor_manager.has_been_processed(
            self.file_path, function_node_id
        ):
            for child in node.body.body:
                if isinstance(child, libcst.FunctionDef):
                    function_node_id: str = get_function_id(
                        function_node=child,
                        parent_id=self.model_id,
                        visitor_manager=self.visitor_manager,
                    )

                    if not self.visitor_manager.has_been_processed(
                        self.file_path, function_node_id
                    ):
                        function_visitor = FunctionDefVisitor(
                            parent_id=self.model_id,
                            parent_visitor_instance=self,
                            function_name=child.name.value,
                            function_id=function_node_id,
                            position_metadata=self.position_metadata,
                            module_code_content=self.module_code_content,
                        )
                        child.visit(function_visitor)

            function_name: str = self.model_builder.function_attributes.function_name

            docstring: str | None = node.get_docstring()
            if docstring:
                self.model_builder.set_docstring(docstring)

            position_data: dict[str, int] | None = get_function_position_data(
                function_name, self.position_metadata
            )
            if position_data:
                self.model_builder.set_block_start_line_number(
                    position_data["start_line_number"]
                ).set_block_end_line_number(position_data["end_line_number"])

                code_content: str = extract_code_content(
                    self.module_code_content,
                    position_data["start_line_number"],
                    position_data["end_line_number"],
                )
                self.model_builder.set_code_content(code_content)

            decorator_list: list[DecoratorModel] = extract_decorators(node.decorators)
            for decorator in decorator_list:
                self.model_builder.add_decorator(decorator)

    def visit_Parameters(self, node: libcst.Parameters) -> None:
        print(
            f"\nParameters for {self.model_builder.function_attributes.function_name}:\n"
        )

        # TODO: Add model construction and add to builder logic
        if node.params:
            parameters: list[str] | None = get_parameters_list(node.params)
            print(f"Parameters: {parameters}")

        if node.star_arg:
            if isinstance(node.star_arg, libcst.Param):
                star: str = str(node.star_arg.star)
                star_arg: str = extract_and_process_parameter(node.star_arg, star=star)
                print(f"Star arg: {star_arg}")

        if node.kwonly_params:
            kwonly_params: list[str] | None = get_parameters_list(node.kwonly_params)
            print(f"Kwonly params: {kwonly_params}")

        if node.star_kwarg:
            stars: str = str(node.star_kwarg.star)
            star_kwarg: str = extract_and_process_parameter(node.star_kwarg, star=stars)
            print(f"Star kwarg: {star_kwarg}")

        if node.posonly_params:
            posonly_params: list[str] | None = get_parameters_list(node.posonly_params)
            print(f"Posonly params: {posonly_params}")

    def visit_Comment(self, node: libcst.Comment) -> None:
        process_comment(node, self.model_builder)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: FunctionModel = self.model_builder.build()  # type: ignore
            self.add_child_to_parent_visitor(built_model)
