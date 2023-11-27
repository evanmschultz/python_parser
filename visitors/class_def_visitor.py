# TODO: get and set attributes logic, requires the FunctionDefVisitor for `__init__` methods, and custom logic for other types of classes

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Sequence, Union
import libcst
from libcst import CSTNode, ClassDef
from libcst.metadata import CodeRange

from model_builders.class_model_builder import ClassModelBuilder
from models.enums import BlockType
from visitors.base_code_block_visitor import BaseCodeBlockVisitor

from models.models import (
    ClassKeywordModel,
    ClassModel,
    DecoratorModel,
)
from visitors.node_processing.class_def_functions import (
    get_and_set_class_bases,
    get_and_set_class_keywords,
    get_class_id,
    get_class_position_data,
)
from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_decorators,
    process_comment,
)
from visitors.node_processing.function_def_functions import get_function_id
from visitors.visitor_manager import VisitorManager
from visitors.function_def_visitor import FunctionDefVisitor

if TYPE_CHECKING:
    from visitors.module_visitor import ModuleVisitor
    from models.models import (
        FunctionModel,
        StandaloneCodeBlockModel,
    )


class ClassDefVisitor(BaseCodeBlockVisitor):
    """
    A visitor class for processing `ClassDef` nodes in the AST.

    This class extends the `BaseCodeBlockVisitor` and is responsible for visiting
    and processing `ClassDef` nodes, building the corresponding class model, and
    managing child visitors.

    Attributes:
        parent_id (str): The ID of the parent code block.
        parent_visitor_instance (BaseCodeBlockVisitor): The instance of the parent visitor.
        class_name (str): The name of the class being visited.
        class_id (str): The ID of the class being visited.
        file_path (str): The file path of the code being visited.
        model_builder (ClassModelBuilder): The model builder for the class being visited.
        visitor_manager (VisitorManager): The visitor manager for managing child visitors.
    """

    def __init__(
        self,
        parent_id: str,
        parent_visitor_instance: Union[ModuleVisitor, "ClassDefVisitor"],
        class_name: str,
        class_id: str,
        position_metadata: Mapping[CSTNode, CodeRange],
        module_code_content: str,
    ) -> None:
        super().__init__(
            model_builder=ClassModelBuilder(
                parent_id=parent_id,
                class_name=class_name,
                class_id=class_id,
            ),
            file_path=parent_visitor_instance.file_path,
            parent_visitor_instance=parent_visitor_instance,
            model_id=class_id,
        )
        self.parent_id: str = parent_id
        self.model_builder: ClassModelBuilder = self.model_builder
        self.visitor_manager: VisitorManager = VisitorManager.get_instance()
        self.position_metadata: Mapping[CSTNode, CodeRange] = position_metadata
        self.module_code_content: str = module_code_content

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        class_node_id: str = get_class_id(
            class_node=node,
            parent_id=self.model_id,
            visitor_manager=self.visitor_manager,
        )

        if not self.visitor_manager.has_been_processed(self.file_path, class_node_id):
            for child in node.body.body:
                if isinstance(child, libcst.ClassDef):
                    class_node_id: str = get_class_id(
                        class_node=child,
                        parent_id=self.model_id,
                        visitor_manager=self.visitor_manager,
                    )

                    if not self.visitor_manager.has_been_processed(
                        self.file_path, class_node_id
                    ):
                        class_name: str = child.name.value
                        class_visitor = ClassDefVisitor(
                            parent_id=self.model_id,
                            parent_visitor_instance=self,
                            class_name=class_name,
                            class_id=class_node_id,
                            position_metadata=self.position_metadata,
                            module_code_content=self.module_code_content,
                        )
                        child.visit(class_visitor)

                if isinstance(child, libcst.FunctionDef):
                    function_id: str = get_function_id(
                        child, self.model_id, self.visitor_manager
                    )

                    if not self.visitor_manager.has_been_processed(
                        self.file_path, function_id
                    ):
                        function_name: str = child.name.value
                        class_visitor = FunctionDefVisitor(
                            parent_id=self.model_id,
                            parent_visitor_instance=self,
                            function_name=function_name,
                            function_id=function_id,
                            position_metadata=self.position_metadata,
                            module_code_content=self.module_code_content,
                        )
                        child.visit(class_visitor)

            # TODO: From here Function

            class_name: str = self.model_builder.class_attributes.class_name

            docstring: str | None = node.get_docstring()
            if docstring:
                self.model_builder.set_docstring(docstring)

            position_data: dict[str, int] | None = get_class_position_data(
                class_name, self.position_metadata
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

            get_and_set_class_bases(node.bases, self.model_builder)
            get_and_set_class_keywords(node.keywords, self.model_builder)

    def visit_Comment(self, node: libcst.Comment) -> None:
        process_comment(node, self.model_builder)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: ClassModel | FunctionModel | StandaloneCodeBlockModel = self.model_builder.build()  # type: ignore
            self.add_child_to_parent_visitor(built_model)
