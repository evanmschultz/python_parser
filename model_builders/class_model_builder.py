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

    def set_decorator_list(
        self, decorator_list: list[DecoratorModel]
    ) -> "ClassModelBuilder":
        """Sets the list of decorators in the function model."""
        self.class_attributes.decorators = decorator_list
        return self

    def set_base_class_list(self, base_classes: list[str]) -> "ClassModelBuilder":
        """Sets the list of base classes to the class model."""
        self.class_attributes.base_classes = base_classes
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

    def set_keywords(
        self, keyword_list: list[ClassKeywordModel] | None
    ) -> "ClassModelBuilder":
        """Sets the list of keywords to the class model."""
        if keyword_list:
            self.class_attributes.keywords = keyword_list
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
