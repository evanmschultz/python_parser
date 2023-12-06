from typing import Any

from logger.decorators import logging_decorator
from model_builders.base_model_builder import BaseModelBuilder
from models.enums import BlockType
from models.models import (
    StandaloneCodeBlockModel,
    StandaloneCodeBlockSpecificAttributes,
)


class StandaloneBlockModelBuilder(BaseModelBuilder):
    """
    A builder class for constructing a model of a standalone code block.

    This class extends BaseModelBuilder and specializes in building models of standalone code blocks, which are blocks of code not part of any class or function definitions. It captures details such as variable assignments within the block.

    Attributes:
        standalone_block_attributes (StandaloneCodeBlockSpecificAttributes): An instance containing attributes specific to a standalone code block, such as variable assignments.

    Args:
        id (str): The unique identifier for the standalone code block model.
        parent_id (str): The identifier of the parent model (e.g., module or class containing this standalone block).

    Example:
        >>> standalone_block_builder = StandaloneBlockModelBuilder(id='block1', parent_id='module1')
        >>> standalone_block_builder.set_variable_assignments(['x = 1', 'y = 2'])
        # Configures the builder with variable assignments for the standalone code block.
    """

    def __init__(self, id: str, parent_id: str) -> None:
        super().__init__(
            id=id, block_type=BlockType.STANDALONE_CODE_BLOCK, parent_id=parent_id
        )

        self.standalone_block_attributes = StandaloneCodeBlockSpecificAttributes(
            variable_assignments=None,
        )

    def set_variable_assignments(
        self, variable_declarations: list[str]
    ) -> "StandaloneBlockModelBuilder":
        """Sets the list of variable declarations to the standalone code block model."""
        self.standalone_block_attributes.variable_assignments = variable_declarations
        return self

    def _get_standalone_block_specific_attributes(self) -> dict[str, Any]:
        """Gets the standalone block specific attributes."""
        return self.standalone_block_attributes.model_dump()

    @logging_decorator(message="Building standalone code block model")
    def build(self) -> StandaloneCodeBlockModel:
        """Creates a StandaloneCodeBlockModel instance after building and setting the children models."""
        return StandaloneCodeBlockModel(
            **self._get_common_attributes(),
            **self._get_standalone_block_specific_attributes(),
        )
