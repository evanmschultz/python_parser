from typing import Any

from logger.decorators import logging_decorator
from model_builders.base_model_builder import BaseModelBuilder
from models.enums import BlockType
from models.models import (
    StandaloneCodeBlockModel,
    StandaloneCodeBlockSpecificAttributes,
)


class StandaloneBlockModelBuilder(BaseModelBuilder):
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
        """Creates a StandaloneCodeBlockModel instance."""
        return StandaloneCodeBlockModel(
            **self._get_common_attributes(),
            **self._get_standalone_block_specific_attributes(),
        )
