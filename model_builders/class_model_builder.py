from __future__ import annotations
from typing import TYPE_CHECKING, Any
from logger.decorators import logging_decorator

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
    """
    A builder class for constructing a model of a Python class.

    This class extends BaseModelBuilder and is specialized for building a model of a Python class, capturing details such as decorators, base classes, documentation strings, class attributes, and class-specific keywords.

    Attributes:
        class_attributes (ClassSpecificAttributes): An instance containing attributes specific to a class, like name, decorators, bases, etc.

    Args:
        id (str): The unique identifier for the class model.
        class_name (str): The name of the class.
        parent_id (str): The identifier of the parent model (e.g., module or class containing this class).
    """

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

    def set_bases(self, base_classes: list[str] | None) -> "ClassModelBuilder":
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

    @logging_decorator(message="Building ClassModel")
    def build(self) -> ClassModel:
        """Creates a ClassModel instance after building and setting the children models."""
        self.build_and_set_children()
        return ClassModel(
            **self._get_common_attributes(),
            **self._get_class_specific_attributes(),
        )
