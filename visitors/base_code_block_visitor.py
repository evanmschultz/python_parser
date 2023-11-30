# TODO: get and set dependencies logic

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Union
import libcst


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
        FunctionModel,
        StandaloneCodeBlockModel,
    )


class BaseCodeBlockVisitor(libcst.CSTVisitor, ABC):
    """
    Abstract base class for all code block visitors.

    This class provides common functionalities for all visitors, such as integration with VisitorManager
    to track processed nodes.

    Attributes:
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
        model_id: str,
        parent_visitor_instance: Union[
            "ClassDefVisitor", "FunctionDefVisitor", "ModuleVisitor", None
        ] = None,
    ) -> None:
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

    def not_added_to_parent_visitor(self, child_id: str) -> bool:
        if self.parent_visitor_instance:
            return child_id not in self.parent_visitor_instance.children_ids_set
        else:
            raise Exception("Parent visitor instance not set.")

    def add_built_model_to_parent_visitor(
        self, built_model: ClassModel | FunctionModel | StandaloneCodeBlockModel
    ) -> None:
        if self.parent_visitor_instance:
            self.parent_visitor_instance.children.append(built_model)

            if built_model.id:
                self.parent_visitor_instance.children_ids_set.add(built_model.id)
