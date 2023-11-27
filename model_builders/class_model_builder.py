from __future__ import annotations
from typing import TYPE_CHECKING, Any

from model_builders.base_model_builder import BaseModelBuilder
from models.models import ClassSpecificAttributes, ClassModel
from models.enums import BlockType, ClassType


if TYPE_CHECKING:
    from models.models import (
        ClassKeywordModel,
        DecoratorModel,
        BlockType,
        ClassType,
    )


class ClassModelBuilder(BaseModelBuilder):
    """
    Class for building class models. Uses the builder pattern to allow for construction the model step-by-step.

    params:
        parent_id: The id of the parent model.
    """

    def __init__(self, parent_id: str, class_name: str, class_id: str) -> None:
        super().__init__(
            parent_id=parent_id,
            block_type=BlockType.CLASS,
            block_id=class_id,
        )

        self.class_attributes = ClassSpecificAttributes(
            class_name=class_name,
            decorators=None,
            base_classes=None,
            class_type=ClassType.STANDARD,
            docstring=None,
            attributes=None,
            keywords=None,
        )

    def set_class_name(self, class_name: str) -> "ClassModelBuilder":
        """Sets the name of the class in the model."""
        self.class_attributes.class_name = class_name
        return self

    def add_decorator(self, decorator: DecoratorModel) -> "ClassModelBuilder":
        """Adds a decorator to the class model."""
        if not self.class_attributes.decorators:
            self.class_attributes.decorators = []
        self.class_attributes.decorators.append(decorator)
        return self

    def add_base_class(self, base_class: str) -> "ClassModelBuilder":
        """Adds a base class to the class model."""
        if not self.class_attributes.base_classes:
            self.class_attributes.base_classes = []
        self.class_attributes.base_classes.append(base_class)
        return self

    def set_class_type(self, class_type: ClassType) -> "ClassModelBuilder":
        """Sets the type of the class in the model."""
        self.class_attributes.class_type = class_type
        return self

    def set_docstring(self, docstring: str | None) -> "ClassModelBuilder":
        """Sets the docstring of the class in the model."""
        if docstring:
            self.class_attributes.docstring = docstring
        return self

    # TODO: Add attribute model
    def add_attribute(self, attribute) -> "ClassModelBuilder":
        """Adds an attribute of the class in the model."""
        if not self.class_attributes.attributes:
            self.class_attributes.attributes = []
        self.class_attributes.attributes.append(attribute)
        return self

    def add_keyword(self, keyword: ClassKeywordModel) -> "ClassModelBuilder":
        """Adds a keyword of the class in the model."""
        if not self.class_attributes.keywords:
            self.class_attributes.keywords = []
        self.class_attributes.keywords.append(keyword)
        return self

    def _get_class_specific_attributes(self) -> dict[str, Any]:
        """Gets the class specific attributes."""
        return self.class_attributes.model_dump()

    def _create_model_instance(self) -> ClassModel:
        """Creates a ClassModel instance."""
        return ClassModel(
            **self._get_common_attributes(),
            **self._get_class_specific_attributes(),
        )
