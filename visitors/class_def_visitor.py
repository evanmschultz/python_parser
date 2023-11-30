# TODO: get and set attributes logic, requires the FunctionDefVisitor for `__init__` methods, and custom logic for other types of classes

from __future__ import annotations
from functools import partial

from typing import TYPE_CHECKING, Mapping, Union
import libcst
from libcst import CSTNode
from libcst.metadata import CodeRange

from model_builders.class_model_builder import ClassModelBuilder
from models.enums import BlockType
from visitors.base_code_block_visitor import BaseCodeBlockVisitor

from models.models import (
    ClassKeywordModel,
    ClassModel,
    CommentModel,
    DecoratorModel,
)
from visitors.node_processing.class_def_functions import (
    extract_bases_from_class,
    extract_class_keywords,
    get_class_id_context,
)
from visitors.node_processing.common_functions import (
    PositionData,
    extract_important_comments,
    get_node_id,
    get_node_position_data,
    extract_code_content,
    extract_decorators,
)
from visitors.node_processing.function_def_functions import (
    get_function_id_context,
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
        model_builder (ClassModelBuilder): The model builder for the class being visited.
        visitor_manager (VisitorManager): The visitor manager for managing child visitors.
    """

    def __init__(
        self,
        parent_id: str,
        parent_visitor_instance: Union[ModuleVisitor, "ClassDefVisitor"],
        class_name: str,
        class_id: str,
        module_id: str,
        position_metadata: Mapping[CSTNode, CodeRange],
        module_code_content: str,
    ) -> None:
        super().__init__(
            model_builder=ClassModelBuilder(
                parent_id=parent_id,
                class_name=class_name,
                class_id=class_id,
            ),
            parent_visitor_instance=parent_visitor_instance,
            model_id=class_id,
        )
        self.module_id: str = module_id
        self.parent_id: str = parent_id
        self.model_builder: ClassModelBuilder = self.model_builder
        self.visitor_manager: VisitorManager = VisitorManager.get_instance()
        self.position_metadata: Mapping[CSTNode, CodeRange] = position_metadata
        self.module_code_content: str = module_code_content
        self.node_id_generator = partial(
            get_node_id,
            node_type=BlockType.CLASS,
        )

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        """Visits the class definition and recursively visits the children (ClassDefs and FunctionDefs)."""
        class_name: str = self.model_builder.class_attributes.class_name

        docstring: str | None = node.get_docstring()
        if docstring:
            self.model_builder.set_docstring(docstring)

        position_data: PositionData = get_node_position_data(
            class_name, self.position_metadata
        )
        code_content: str = extract_code_content(node)
        decorator_list: list[DecoratorModel] = extract_decorators(node.decorators)
        base_classes: list[str] | None = extract_bases_from_class(node.bases)
        key_words: list[ClassKeywordModel] | None = extract_class_keywords(
            node.keywords
        )

        (
            self.model_builder.set_block_start_line_number(position_data.start)
            .set_block_end_line_number(position_data.end)
            .set_code_content(code_content)
            .set_decorator_list(decorator_list)  # type: ignore
            .set_base_class_list(base_classes)  # type: ignore
            .set_keywords(key_words)
        )

        important_comments: list[CommentModel] = extract_important_comments(node)
        self.model_builder.set_important_comments(important_comments)

        for child in node.body.body:
            if isinstance(child, libcst.ClassDef):
                id_context: dict[str, str] = get_class_id_context(
                    child.name.value,
                    self.model_id,
                )
                child_node_id: str = self.node_id_generator(context=id_context)
                child_class_code_content: str = extract_code_content(child)

                if not self.visitor_manager.has_been_processed(
                    self.module_id, child_class_code_content
                ):
                    class_name: str = child.name.value
                    class_visitor = ClassDefVisitor(
                        parent_id=self.model_id,
                        parent_visitor_instance=self,
                        class_name=class_name,
                        class_id=child_node_id,
                        module_id=self.module_id,
                        position_metadata=self.position_metadata,
                        module_code_content=self.module_code_content,
                    )
                    child.visit(class_visitor)

            if isinstance(child, libcst.FunctionDef):
                function_id_context: dict[str, str] = get_function_id_context(
                    function_name=child.name.value,
                    parent_id=self.model_id,
                )
                function_id: str = get_node_id(
                    node_type=BlockType.FUNCTION, context=function_id_context
                )
                child_function_code_content: str = extract_code_content(child)

                if not self.visitor_manager.has_been_processed(
                    self.module_id, child_function_code_content
                ):
                    function_name: str = child.name.value
                    class_visitor = FunctionDefVisitor(
                        parent_id=self.model_id,
                        parent_visitor_instance=self,
                        function_name=function_name,
                        function_id=function_id,
                        module_id=self.module_id,
                        position_metadata=self.position_metadata,
                        module_code_content=self.module_code_content,
                    )
                    child.visit(class_visitor)

    # def visit_Comment(self, node: libcst.Comment) -> None:
    #     """Visits the comments in the class definition, processes them, and sets them in the model builder."""
    #     process_comment(node, self.model_builder)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        """Builds the class model and adds it to the parent visitor."""
        for child in self.children:
            self.model_builder.add_child(child)
        if self.not_added_to_parent_visitor(self.model_id):
            built_model: ClassModel | FunctionModel | StandaloneCodeBlockModel = self.model_builder.build()  # type: ignore
            self.add_built_model_to_parent_visitor(built_model)
