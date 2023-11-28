# TODO: method_type logic
# TODO: Fix type hinting errors

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Union
import libcst
from libcst import CSTNode
from libcst.metadata import CodeRange

from model_builders.function_model_builder import FunctionModelBuilder
from models.enums import BlockType
from visitors.base_code_block_visitor import BaseCodeBlockVisitor

from models.models import (
    FunctionModel,
    ParameterListModel,
)
from visitors.node_processing.function_def_functions import (
    extract_and_process_return_annotation,
    extract_star_parameter,
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

    from models.models import (
        DecoratorModel,
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
        """Visits the function definition and recursively visits the children."""

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
            docstring: str | None = node.get_docstring()
            return_annotation: str = extract_and_process_return_annotation(node.returns)
            is_method: bool = self.is_method()

            if node.asynchronous:
                self.model_builder.set_is_async(True)

            (
                self.model_builder.set_docstring(docstring)
                .set_decorator_list(decorator_list)
                .set_is_method(is_method)
                .set_return_annotation(return_annotation)
            )

    def visit_Parameters(self, node: libcst.Parameters) -> None:
        """Visits the parameters of a function definition and sets the model in the builder instance."""

        params: list[ParameterModel] | None = (
            get_parameters_list(node.params) if node.params else None
        )
        kwonly_params: list[ParameterModel] | None = (
            get_parameters_list(node.kwonly_params) if node.kwonly_params else None
        )
        posonly_params: list[ParameterModel] | None = (
            get_parameters_list(node.posonly_params) if node.posonly_params else None
        )
        star_arg: ParameterModel | None = (
            extract_star_parameter(node.star_arg)
            if node.star_arg and isinstance(node.star_arg, libcst.Param)
            else None
        )
        star_kwarg: ParameterModel | None = (
            extract_star_parameter(node.star_kwarg) if node.star_kwarg else None
        )
        self.model_builder.add_parameters_list(
            ParameterListModel(
                params=params,
                star_arg=star_arg,
                kwonly_params=kwonly_params,
                star_kwarg=star_kwarg,
                posonly_params=posonly_params,
            )
        )

    def visit_Comment(self, node: libcst.Comment) -> None:
        """Visits the comment of a function definition and sets the model in the builder instance."""
        process_comment(node, self.model_builder)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        """Builds the function model and adds it to the parent visitor instance."""
        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: FunctionModel = self.model_builder.build()  # type: ignore
            self.add_child_to_parent_visitor(built_model)

    def is_method(self) -> bool:
        """Returns true if an ancestor of the function is a class."""

        ancestor: ClassDefVisitor | FunctionDefVisitor | ModuleVisitor = (
            self.parent_visitor_instance
        )  # type: ignore # TODO: Fix type hinting error

        while ancestor.model_builder.common_attributes.block_type != BlockType.MODULE:
            if ancestor.model_builder.common_attributes.block_type == BlockType.CLASS:
                return True
            ancestor = ancestor.parent_visitor_instance  # type: ignore # TODO: Fix type hinting error
        return False
