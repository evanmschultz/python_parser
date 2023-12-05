from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union
from abc import ABC, abstractmethod

from models.models import (
    BaseCodeBlockModel,
    CommentModel,
    BlockType,
)

if TYPE_CHECKING:
    from model_builders.class_model_builder import ClassModelBuilder
    from model_builders.function_model_builder import FunctionModelBuilder
    from model_builders.module_model_builder import ModuleModelBuilder
    from model_builders.standalone_block_model_builder import (
        StandaloneBlockModelBuilder,
    )


class BaseModelBuilder(ABC):
    def __init__(
        self, *, id: str, block_type: BlockType, parent_id: str | None
    ) -> None:
        self.id: str = id
        self.children_builders: list[ClassModelBuilder | FunctionModelBuilder] = []

        self.common_attributes = BaseCodeBlockModel(
            id=id,
            parent_id=parent_id,
            block_type=block_type,
            start_line_num=0,
            end_line_num=0,
            code_content="",
            important_comments=None,
            children=None,
            dependencies=None,
            summary=None,
        )

    def set_start_line_num(
        self, line_num: int
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the start line number of the code block model instance."""
        self.common_attributes.start_line_num = line_num
        return self

    def set_end_line_num(
        self, line_num: int
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the end line number of the code block model instance."""
        self.common_attributes.end_line_num = line_num
        return self

    def set_code_content(
        self, code_content: str
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds the string containing the content of the code block to the model instance."""
        self.common_attributes.code_content = code_content
        return self

    def add_important_comment(
        self, comment: CommentModel
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds an important comment to the model instance."""
        if not self.common_attributes.important_comments:
            self.common_attributes.important_comments = []
        self.common_attributes.important_comments.append(comment)
        return self

    def add_summary(
        self, summary: str
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds a summary to the model instance."""
        return self

    def add_child(
        self,
        child: Union[
            "ClassModelBuilder", "FunctionModelBuilder", StandaloneBlockModelBuilder
        ],
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds a child code block to the model instance."""
        self.children_builders.append(child)  # type: ignore # TODO: Remove type ignore when stand alone code block model is added
        return self

    def build_and_set_children(self) -> None:
        if self.children_builders:
            self.common_attributes.children = [
                child.build() for child in self.children_builders
            ]

    def _get_common_attributes(self) -> dict[str, Any]:
        """
        Returns a dictionary containing the attributes common to all code block models.
        """
        return self.common_attributes.model_dump()

    @abstractmethod
    def build(
        self,
    ) -> None:
        """
        Builds and returns the code block model instance.

        Returns:
            CodeBlockModel: The built code block model instance.
        """
        ...
