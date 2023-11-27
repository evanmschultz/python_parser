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
        class_node_id: str = self.get_class_id(
            class_node=node,
            parent_id=self.model_id,
            visitor_manager=self.visitor_manager,
        )

        if not self.visitor_manager.has_been_processed(self.file_path, class_node_id):
            for child in node.body.body:
                if isinstance(child, libcst.ClassDef):
                    class_node_id: str = self.get_class_id(
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
                    function_id: str = FunctionDefVisitor.get_function_id(
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

            position_data: dict[str, int] | None = self.get_class_position_data(
                class_name, self.position_metadata
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

            self.get_and_set_class_bases(node.bases, self.model_builder)
            self.get_and_set_class_keywords(node.keywords, self.model_builder)

    def visit_Comment(self, node: libcst.Comment) -> None:
        ClassDefVisitor.process_comment(node, self.model_builder)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: ClassModel | FunctionModel | StandaloneCodeBlockModel = self.model_builder.build()  # type: ignore
            self.add_child_to_parent_visitor(built_model)

    @staticmethod
    def get_class_id(
        class_node: libcst.ClassDef, parent_id: str, visitor_manager: VisitorManager
    ) -> str:
        """
        Get the unique identifier for a class node.

        Args:
            child (libcst.ClassDef): The class node.
            parent_id (str): The identifier of the parent node.
            visitor_manager (VisitorManager): The visitor manager.

        Returns:
            str: The unique identifier for the class node.
        """
        id_generation_context: dict[str, str] = {
            "parent_id": parent_id,
            "class_name": class_node.name.value,
        }
        class_node_id: str = visitor_manager.get_node_id(
            BlockType.CLASS, id_generation_context
        )
        return class_node_id

    @staticmethod
    def get_class_position_data(
        node_name: str, position_metadata: Mapping[CSTNode, CodeRange]
    ) -> dict[str, int] | None:
        position_data: dict[str, int] | None = None

        for item in position_metadata:
            if type(item) is ClassDef and item.name.value == node_name:
                start_line_number: int = position_metadata[item].start.line
                end_line_number: int = position_metadata[item].end.line

                position_data = {
                    "start_line_number": start_line_number,
                    "end_line_number": end_line_number,
                }

        if position_data:
            return position_data
        else:
            raise Exception(
                "Class position data not found. Check logic in `get_and_set_class_position_data`!"
            )

    @staticmethod
    def get_and_set_class_bases(
        bases: Sequence[libcst.Arg], model_builder: ClassModelBuilder
    ) -> None:
        for base in bases:
            if isinstance(base, libcst.Arg):
                arg_value: str | None = None
                if isinstance(base.value, libcst.Name):
                    arg_value = base.value.value

                if arg_value:
                    model_builder.add_base_class(arg_value)

    @staticmethod
    def get_and_set_class_keywords(
        keywords: Sequence[libcst.Arg], model_builder: ClassModelBuilder
    ) -> None:
        for keyword_arg in keywords:
            if isinstance(keyword_arg, libcst.Arg):
                keyword: str | None = (
                    keyword_arg.keyword.value if keyword_arg.keyword else None
                )

                if isinstance(keyword_arg.value, libcst.Name):
                    arg_value: str = keyword_arg.value.value
                elif isinstance(keyword_arg.value, libcst.Integer):
                    arg_value = str(keyword_arg.value.value)
                else:
                    arg_value = str(keyword_arg.value)

                if keyword and arg_value:
                    model_builder.add_keyword(
                        ClassKeywordModel(keyword_name=keyword, arg_value=arg_value)
                    )
                else:
                    raise Exception(
                        "Keyword or argument value not found for class keyword. Check logic in `get_and_set_class_keywords`!"
                    )
