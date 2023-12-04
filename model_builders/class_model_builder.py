from __future__ import annotations
from typing import TYPE_CHECKING, Any

from model_builders.base_model_builder import BaseModelBuilder
from models.models import ClassSpecificAttributes, ClassModel
from models.enums import BlockType


if TYPE_CHECKING:
    from models.models import (
        ClassKeywordModel,
        DecoratorModel,
        BlockType,
    )


class ClassModelBuilder(BaseModelBuilder):
    def __init__(self, id: str, class_name: str, parent_id: str) -> None:
        super().__init__(id=id, block_type=BlockType.CLASS, parent_id=parent_id)

        self.class_attributes = ClassSpecificAttributes(
            class_name=class_name,
            decorators=None,
            bases=None,
            docstring=None,
            attributes=None,
            keywords=None,
        )

    def set_decorators(
        self, decorators: list[DecoratorModel] | None
    ) -> "ClassModelBuilder":
        """Adds decorator to the decorators list in the class model."""
        if decorators:
            self.class_attributes.decorators = decorators
        else:
            self.class_attributes.decorators = None
        return self

    def set_bases(self, base_classes: list[str]) -> "ClassModelBuilder":
        """Sets the list of base classes to the class model."""
        self.class_attributes.bases = base_classes
        return self

    def set_docstring(self, docstring: str | None) -> "ClassModelBuilder":
        """Sets the docstring of the class in the model."""
        self.class_attributes.docstring = docstring
        return self

    # TODO: Add attribute model
    def add_attribute(self, attribute) -> "ClassModelBuilder":
        """Adds an attribute of the class in the model."""
        if not self.class_attributes.attributes:
            self.class_attributes.attributes = []
        self.class_attributes.attributes.append(attribute)
        return self

    def set_keywords(
        self, keyword_list: list[ClassKeywordModel] | None
    ) -> "ClassModelBuilder":
        """Sets the list of keywords to the class model."""
        self.class_attributes.keywords = keyword_list
        return self

    def _get_class_specific_attributes(self) -> dict[str, Any]:
        """Gets the class specific attributes."""
        return self.class_attributes.model_dump()

    def build(self) -> ClassModel:
        """Creates a ClassModel instance."""
        self.build_and_set_children()
        return ClassModel(
            **self._get_common_attributes(),
            **self._get_class_specific_attributes(),
        )
