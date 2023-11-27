# TODO: get and set dependencies logic

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Sequence, Union
import libcst
from models.models import DecoratorModel

from utilities.comment_extractor import CommentExtractor

if TYPE_CHECKING:
    from visitors.class_def_visitor import ClassDefVisitor
    from visitors.function_def_visitor import FunctionDefVisitor
    from visitors.module_visitor import ModuleVisitor

    from model_builders.class_model_builder import ClassModelBuilder
    from model_builders.function_model_builder import FunctionModelBuilder
    from model_builders.module_model_builder import ModuleModelBuilder
    from model_builders.standalone_code_block_model_builder import (
        StandaloneCodeBlockModelBuilder,
    )

    from models.models import (
        ClassModel,
        CommentModel,
        FunctionModel,
        StandaloneCodeBlockModel,
    )


class BaseCodeBlockVisitor(libcst.CSTVisitor, ABC):
    """
    Abstract base class for all code block visitors.

    This class provides common functionalities for all visitors, such as integration with VisitorManager
    to track processed nodes.

    Attributes:
        file_path (str): File path of the module being visited.
        model_builder (BaseModelBuilder): Builder for the code block model.
        id (str): Identifier of the visitor.
        parent_visitor_instance (BaseCodeBlockVisitor): Reference to the parent visitor instance.
        children (list[BaseCodeBlockModel]): List of child models built by this visitor.
    """

    def __init__(
        self,
        model_builder: Union[
            "ClassModelBuilder",
            "FunctionModelBuilder",
            "ModuleModelBuilder",
            "StandaloneCodeBlockModelBuilder",
        ],
        file_path: str,
        model_id: str,
        parent_visitor_instance: Union[
            "ClassDefVisitor", "FunctionDefVisitor", "ModuleVisitor", None
        ] = None,
    ) -> None:
        self.file_path: str = file_path
        self.model_builder: Union[
            "ClassModelBuilder",
            "FunctionModelBuilder",
            "ModuleModelBuilder",
            "StandaloneCodeBlockModelBuilder",
        ] = model_builder
        self.model_id: str = model_id
        self.parent_visitor_instance: ClassDefVisitor | FunctionDefVisitor | ModuleVisitor | None = (
            parent_visitor_instance
        )
        self.children: list[ClassModel | FunctionModel | StandaloneCodeBlockModel] = []
        self.children_ids_set: set[str] = set()

    @staticmethod
    def process_comment(
        node: libcst.CSTNode,
        model_builder: ClassModelBuilder
        | FunctionModelBuilder
        | ModuleModelBuilder
        | StandaloneCodeBlockModelBuilder,
    ) -> None:
        important_comment: CommentModel | None = CommentExtractor.get_important_comment(
            node
        )
        if important_comment:
            model_builder.add_important_comment(important_comment)

    def not_added_to_parent_visitor(self, child_id: str) -> bool:
        if self.parent_visitor_instance:
            return child_id not in self.parent_visitor_instance.children_ids_set
        else:
            raise Exception("Parent visitor instance not set.")

    def add_child_to_parent_visitor(
        self, child_model: ClassModel | FunctionModel | StandaloneCodeBlockModel
    ) -> None:
        if self.parent_visitor_instance:
            self.parent_visitor_instance.children.append(child_model)

            if child_model.id:
                self.parent_visitor_instance.children_ids_set.add(child_model.id)

    def get_code_content(
        self, module_content: str, start_line_num: int, end_line_num: int
    ) -> str:
        code_content_list: list[str] = module_content.split("\n")[
            start_line_num - 1 : end_line_num
        ]
        code_content: str = "\n".join(code_content_list)

        return code_content

    @staticmethod
    def extract_decorators(
        decorators: Sequence[libcst.Decorator],
    ) -> list[DecoratorModel]:
        """Works for both class and function decorators"""
        decorator_list: list[DecoratorModel] = []

        def extract_function_name_from_decorator(
            decorator: libcst.Decorator,
        ) -> str | None:
            if isinstance(decorator.decorator, libcst.Call):
                if isinstance(decorator.decorator.func, libcst.Name):
                    return decorator.decorator.func.value
            return None

        def extract_arguments_from_decorator(call: libcst.Call) -> list[str]:
            def get_value_from_arg(arg) -> str:
                return str(arg.value.value)

            return [get_value_from_arg(arg) for arg in call.args]

        def process_decorator(decorator: libcst.Decorator) -> None:
            func_name: str | None = extract_function_name_from_decorator(decorator)
            if func_name and isinstance(decorator.decorator, libcst.Call):
                args: list[str] = extract_arguments_from_decorator(decorator.decorator)
                decorator_model = DecoratorModel(
                    decorator_name=func_name, decorator_args=args
                )

                decorator_list.append(decorator_model)

        def handle_non_call_decorators(decorator: libcst.Decorator) -> None:
            if isinstance(decorator.decorator, libcst.Name):
                decorator_model = DecoratorModel(
                    decorator_name=decorator.decorator.value
                )
                decorator_list.append(decorator_model)

        for decorator in decorators:
            if isinstance(decorator.decorator, libcst.Call):
                process_decorator(decorator)
            else:
                handle_non_call_decorators(decorator)

        return decorator_list
