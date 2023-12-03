from typing import Union

import libcst
from libcst.metadata import (
    WhitespaceInclusivePositionProvider,
    CodeRange,
)
from libcst._metadata_dependent import _UNDEFINED_DEFAULT


from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
)
from model_builders.builder_factory import BuilderFactory
from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder

from models.enums import BlockType
from models.models import (
    CommentModel,
    DecoratorModel,
    ImportModel,
    ParameterListModel,
)
from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_important_comment,
)
from visitors.node_processing.function_def_functions import (
    process_func_def,
    process_parameters,
)
from visitors.node_processing.module_functions import (
    extract_content_from_empty_lines,
    process_import,
    process_import_from,
)
from visitors.node_processing.processing_context import PositionData


BuilderType = Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder]


class BaseVisitor(libcst.CSTVisitor):
    METADATA_DEPENDENCIES: tuple[type[WhitespaceInclusivePositionProvider]] = (
        WhitespaceInclusivePositionProvider,
    )

    def __init__(self, id: str) -> None:
        self.id: str = id
        self.builder_stack: list[BuilderType] = []

    def visit_Comment(self, node: libcst.Comment) -> None:
        parent_builder = self.builder_stack[-1]
        content: CommentModel | None = extract_important_comment(node)
        if content:
            parent_builder.add_important_comment(content)

    def get_node_position_data(
        self,
        node: libcst.CSTNode,
    ) -> PositionData:
        position_data: CodeRange | type[_UNDEFINED_DEFAULT] = self.get_metadata(
            WhitespaceInclusivePositionProvider, node
        )

        start, end = 0, 0
        if isinstance(position_data, CodeRange):
            start: int = position_data.start.line
            end: int = position_data.end.line
        return PositionData(start=start, end=end)


class ModuleVisitor(BaseVisitor):
    def __init__(self, id: str, module_builder: ModuleModelBuilder) -> None:
        super().__init__(id)
        self.builder: ModuleModelBuilder = module_builder
        self.builder_stack.append(module_builder)

    def visit_Module(self, node: libcst.Module) -> bool | None:
        docstring: str | None = node.get_docstring()
        header: list[str] = extract_content_from_empty_lines(node.header)
        footer: list[str] = extract_content_from_empty_lines(node.footer)
        content: str = node.code if node.code else ""

        (
            self.builder.set_docstring(docstring)
            .set_header_content(header)
            .set_footer_content(footer)
            .set_code_content(content)
        )

    def visit_Import(self, node: libcst.Import) -> None:
        import_model: ImportModel = process_import(node)
        self.builder.add_import(import_model)

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        import_model: ImportModel = process_import_from(node)
        self.builder.add_import(import_model)

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        parent_id: str = self.builder_stack[-1].id
        class_id: str = ClassIDGenerationStrategy.generate_id(
            parent_id=parent_id, class_name=node.name.value
        )

        class_builder: ClassModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.CLASS,
            name=node.name.value,
            parent_id=parent_id,
        )

        parent_builder: BuilderType = self.builder_stack[-1]
        parent_builder.add_child(class_builder)
        self.builder_stack.append(class_builder)

        docstring: str | None = node.get_docstring()
        code_content: str = extract_code_content(node)
        position_data: PositionData = self.get_node_position_data(node)
        (
            class_builder.set_docstring(docstring)
            .set_code_content(code_content)
            .set_start_line_num(position_data.start)
            .set_end_line_num(position_data.end)
        )

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        self.builder_stack.pop()

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        parent_id: str = self.builder_stack[-1].id
        func_id: str = FunctionIDGenerationStrategy.generate_id(
            parent_id=parent_id, function_name=node.name.value
        )

        func_builder: FunctionModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.FUNCTION,
            name=node.name.value,
            parent_id=parent_id,
        )
        parent_builder: BuilderType = self.builder_stack[-1]
        parent_builder.add_child(func_builder)
        self.builder_stack.append(func_builder)

        position_data: PositionData = self.get_node_position_data(node)
        process_func_def(func_id, node, position_data, func_builder)

    def visit_Decorator(self, node: libcst.Decorator) -> bool | None:
        parent_builder = self.builder_stack[-1]
        if (
            type(parent_builder) == FunctionModelBuilder
            or type(parent_builder) == ClassModelBuilder
        ):
            decorator: DecoratorModel = DecoratorModel(
                content=extract_code_content(node)
            )
            parent_builder.add_decorator(decorator)
        return True

    def visit_Parameters(self, node: libcst.Parameters) -> None:
        builder = self.builder_stack[-1]
        parameter_list: ParameterListModel = process_parameters(node)

        if isinstance(builder, FunctionModelBuilder):
            builder.set_parameters_list(parameter_list)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        self.builder_stack.pop()
