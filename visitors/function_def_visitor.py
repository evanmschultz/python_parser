from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Sequence, Union
import libcst
from libcst import CSTNode, FunctionDef
from libcst.metadata import CodeRange

from model_builders.function_model_builder import FunctionModelBuilder
from models.enums import BlockType
from visitors.base_code_block_visitor import BaseCodeBlockVisitor

from models.models import (
    FunctionModel,
    DecoratorModel,
)
from visitors.visitor_manager import VisitorManager

if TYPE_CHECKING:
    from visitors.class_def_visitor import ClassDefVisitor
    from visitors.module_visitor import ModuleVisitor
    from models.models import (
        ClassModel,
        StandaloneCodeBlockModel,
    )


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
        function_node_id: str = self.get_function_id(
            function_node=node,
            parent_id=self.model_id,
            visitor_manager=self.visitor_manager,
        )

        if not self.visitor_manager.has_been_processed(
            self.file_path, function_node_id
        ):
            for child in node.body.body:
                if isinstance(child, libcst.FunctionDef):
                    function_node_id: str = self.get_function_id(
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

            position_data: dict[str, int] | None = self.get_function_position_data(
                function_name, self.position_metadata
            )
            if position_data:
                self.model_builder.set_block_start_line_number(
                    position_data["start_line_number"]
                ).set_block_end_line_number(position_data["end_line_number"])

                code_content: str = self.get_code_content(
                    self.module_code_content,
                    position_data["start_line_number"],
                    position_data["end_line_number"],
                )
                self.model_builder.set_code_content(code_content)

            decorator_list: list[DecoratorModel] = self.extract_decorators(
                node.decorators
            )
            for decorator in decorator_list:
                self.model_builder.add_decorator(decorator)

    def visit_Parameters(self, node: libcst.Parameters) -> None:
        print(
            f"\nParameters for {self.model_builder.function_attributes.function_name}:\n"
        )

        # TODO: Add model construction and add to builder logic
        if node.params:
            parameters: list[str] | None = FunctionDefVisitor.get_parameters_list(
                node.params
            )

        if node.star_arg:
            if isinstance(node.star_arg, libcst.Param):
                star: str = str(node.star_arg.star)
                star_arg: str = FunctionDefVisitor.extract_and_process_parameter(
                    node.star_arg, star=star
                )

        if node.kwonly_params:
            kwonly_params: list[str] | None = FunctionDefVisitor.get_parameters_list(
                node.kwonly_params
            )

        if node.star_kwarg:
            stars: str = str(node.star_kwarg.star)
            star_kwarg: str = FunctionDefVisitor.extract_and_process_parameter(
                node.star_kwarg, star=stars
            )

        if node.posonly_params:
            posonly_params: list[str] | None = FunctionDefVisitor.get_parameters_list(
                node.posonly_params
            )

    def visit_Comment(self, node: libcst.Comment) -> None:
        FunctionDefVisitor.process_comment(node, self.model_builder)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: FunctionModel = self.model_builder.build()  # type: ignore
            self.add_child_to_parent_visitor(built_model)

    @staticmethod
    def get_parameters_list(
        parameter_sequence: Sequence[libcst.Param],
    ) -> list[str] | None:
        parameters: list[str] = []

        for parameter in parameter_sequence:
            parameter_content: str = FunctionDefVisitor.extract_and_process_parameter(
                parameter
            )
            parameters.append(parameter_content)

        return parameters if parameters else None

    @staticmethod
    def extract_and_process_parameter(
        parameter: libcst.Param, star: str | None = None
    ) -> str:
        name: str = FunctionDefVisitor.get_parameter_name(parameter)
        annotation: str | None = FunctionDefVisitor.extract_type_annotation(parameter)
        default: str | None = FunctionDefVisitor.extract_default(parameter)

        parameter_content: str = FunctionDefVisitor.construct_parameter_content(
            name=name, annotation=annotation, default=default, star=star
        )
        # TODO: Add model logic, to builder
        # return ParameterModel(content=parameter_content)
        return parameter_content

    @staticmethod
    def get_parameter_name(parameter: libcst.Param) -> str:
        return parameter.name.value

    @staticmethod
    def extract_type_annotation(parameter: libcst.Param) -> str | None:
        if isinstance(parameter.annotation, libcst.Annotation):
            return FunctionDefVisitor.handle_annotation_expression(
                expression=parameter.annotation.annotation
            )
        return None

    @staticmethod
    def handle_annotation_expression(expression: libcst.BaseExpression) -> str:
        if isinstance(expression, libcst.Subscript):
            return FunctionDefVisitor.extract_generics_from_type_annotation(expression)
        elif isinstance(expression, libcst.BinaryOperation):
            left: str = FunctionDefVisitor.handle_annotation_expression(expression.left)
            right: str = FunctionDefVisitor.handle_annotation_expression(
                expression.right
            )
            return f"{left} | {right}"
        elif isinstance(expression, libcst.Name):
            return expression.value
        return ""

    @staticmethod
    def extract_generics_from_type_annotation(node: libcst.Subscript) -> str:
        if isinstance(node, libcst.Subscript):
            generics: list[str] = [FunctionDefVisitor.extract_generics_from_type_annotation(element.slice.value) for element in node.slice]  # type: ignore
            return f"{node.value.value}[{', '.join(generics)}]"  # type: ignore

        elif isinstance(node, libcst.Name):
            return node.value

        return ""

    @staticmethod
    def extract_default(parameter: libcst.Param) -> str | None:
        return parameter.default.value if parameter.default else None  # type: ignore

    @staticmethod
    def construct_parameter_content(
        name: str,
        annotation: str | None,
        default: str | None,
        star: str | None = None,
    ) -> str:
        content: str = name

        if star:
            content = f"{star}{name}"
        if annotation:
            content = f"{content}: {annotation}"
        if default:
            content = f"{content} = {default}"
        return content

    @staticmethod
    def get_function_id(
        function_node: libcst.FunctionDef,
        parent_id: str,
        visitor_manager: VisitorManager,
    ) -> str:
        id_generation_context: dict[str, str] = {
            "parent_id": parent_id,
            "function_name": function_node.name.value,
        }
        function_node_id: str = visitor_manager.get_node_id(
            BlockType.FUNCTION, id_generation_context
        )
        return function_node_id

    @staticmethod
    def get_function_position_data(
        node_name: str, position_metadata: Mapping[CSTNode, CodeRange]
    ) -> dict[str, int] | None:
        position_data: dict[str, int] | None = None

        for item in position_metadata:
            if type(item) is FunctionDef and item.name.value == node_name:
                start_line_number: int = position_metadata[item].start.line
                end_line_number: int = position_metadata[item].end.line

                position_data = {
                    "start_line_number": start_line_number,
                    "end_line_number": end_line_number,
                }
                break

        if position_data:
            return position_data
        else:
            raise Exception(
                "Class position data not found. Check logic in `get_and_set_class_position_data`!"
            )
