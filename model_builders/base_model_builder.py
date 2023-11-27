from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union
from abc import ABC, abstractmethod

from models.models import (
    BaseCodeBlockModel,
    ClassModel,
    CommentModel,
    BlockType,
    FunctionModel,
    ModuleModel,
    StandaloneCodeBlockModel,
)

if TYPE_CHECKING:
    from model_builders.class_model_builder import ClassModelBuilder
    from model_builders.function_model_builder import FunctionModelBuilder
    from model_builders.module_model_builder import ModuleModelBuilder
    from model_builders.standalone_code_block_model_builder import (
        StandaloneCodeBlockModelBuilder,
    )


class BaseModelBuilder(ABC):
    """
    Abstract base class for building different types of code block models.

    Args:

        parent_id (str | None): ID of the parent code block.
        block_type (BlockType): Type of the code block.

    Attributes:

        common_attributes (BaseCodeBlockModel): Common attributes for all code block models.
        id_generation_strategy_map (dict[BlockType, type[IDGenerationStrategy]]): Map from block type to
        ID generation strategy.

        common_attributes:

            id (str): ID of the code block.
            parent_id (str | None): ID of the parent code block.
            block_type (BlockType): Type of the code block.
            block_start_line_number (int): Line number of the start of the code block.
            block_end_line_number (int): Line number of the end of the code block.
            content (str): Content of the code block.
            important_comments (list[CommentModel]): List of important comments in the code block.
            children (list[BaseCodeBlockModel]): List of child code blocks.
            dependencies (list[str]): List of dependencies of the code block.
            summary (str | None): Summary of the code block.

    Methods:

        set_block_start_line_number(line_number: int) -> "BaseModelBuilder":
            Sets the start line number of the code block model instance.

        set_block_end_line_number(line_number: int) -> "BaseModelBuilder":
            Sets the end line number of the code block model instance.

        set_content(content: str) -> "BaseModelBuilder":
            Adds the string containing the content of the code block to the model instance.

        add_child(child: BaseCodeBlockModel) -> "BaseModelBuilder":
            Adds a child code block to the model instance.

        add_important_comment(comment: CommentModel) -> "BaseModelBuilder":
            Adds an important comment to the model instance.

        add_summary(summary: str) -> "BaseModelBuilder":
            Adds a summary to the code block model instance.

        build() -> BaseCodeBlockModel:
            Builds and returns the code block model instance.
    """

    def __init__(
        self,
        *,
        parent_id: str | None,
        block_type: BlockType,
        block_id: str,
    ) -> None:
        self.common_attributes = BaseCodeBlockModel(
            id=block_id,
            parent_id=parent_id,
            block_type=block_type,
            block_start_line_number=1,
            block_end_line_number=0,
            code_content="",
            important_comments=None,
            children=None,
            dependencies=None,
            summary=None,
        )

    def set_block_start_line_number(
        self, line_number: int
    ) -> Union[
        "BaseModelBuilder",
        ModuleModelBuilder,
        ClassModelBuilder,
        FunctionModelBuilder,
        StandaloneCodeBlockModelBuilder,
    ]:
        """Sets the start line number of the code block model instance."""
        self.common_attributes.block_start_line_number = line_number
        return self

    def set_block_end_line_number(
        self, line_number: int
    ) -> Union[
        "BaseModelBuilder",
        ModuleModelBuilder,
        ClassModelBuilder,
        FunctionModelBuilder,
        StandaloneCodeBlockModelBuilder,
    ]:
        """Sets the end line number of the code block model instance."""
        self.common_attributes.block_end_line_number = line_number
        return self

    def set_code_content(
        self, code_content: str
    ) -> Union[
        "BaseModelBuilder",
        ModuleModelBuilder,
        ClassModelBuilder,
        FunctionModelBuilder,
        StandaloneCodeBlockModelBuilder,
    ]:
        """Adds the string containing the content of the code block to the model instance."""
        self.common_attributes.code_content = code_content
        return self

    def add_child(
        self,
        child: ClassModel | FunctionModel | StandaloneCodeBlockModel,
    ) -> Union[
        "BaseModelBuilder",
        ModuleModelBuilder,
        ClassModelBuilder,
        FunctionModelBuilder,
        StandaloneCodeBlockModelBuilder,
    ]:
        """Adds a child code block to the model instance."""
        if not self.common_attributes.children:
            self.common_attributes.children = []
        self.common_attributes.children.append(child)
        return self

    def add_important_comment(
        self, comment: CommentModel
    ) -> Union[
        "BaseModelBuilder",
        ModuleModelBuilder,
        ClassModelBuilder,
        FunctionModelBuilder,
        StandaloneCodeBlockModelBuilder,
    ]:
        """Adds an important comment to the model instance."""
        if not self.common_attributes.important_comments:
            self.common_attributes.important_comments = []
        self.common_attributes.important_comments.append(comment)
        return self

    def add_summary(
        self, summary
    ) -> Union[
        "BaseModelBuilder",
        ModuleModelBuilder,
        ClassModelBuilder,
        FunctionModelBuilder,
        StandaloneCodeBlockModelBuilder,
    ]:
        """Adds a summary to the model instance."""
        self.common_attributes.summary = summary
        return self

    def _get_common_attributes(self) -> dict[str, Any]:
        """
        Returns a dictionary containing the attributes common to all code block models.
        """
        return self.common_attributes.model_dump()

    @abstractmethod
    def _create_model_instance(
        self,
    ) -> ClassModel | FunctionModel | ModuleModel | StandaloneCodeBlockModel:
        """
        Abstract method (template) to create an instance of the specific code block model.
        This method must be implemented by the subclasses.
        """
        ...

    def build(
        self,
    ) -> ClassModel | FunctionModel | ModuleModel | StandaloneCodeBlockModel:
        """
        Builds and returns the code block model instance.

        Returns:
            CodeBlockModel: The built code block model instance.
        """
        model_instance: ClassModel | FunctionModel | ModuleModel | StandaloneCodeBlockModel = (
            self._create_model_instance()
        )
        return model_instance

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Builder"
