# TODO: Add `set_method_type` method.

from typing import Any
from models.models import (
    DecoratorModel,
    FunctionModel,
    FunctionSpecificAttributes,
    ParameterListModel,
    BlockType,
)
from model_builders.base_model_builder import BaseModelBuilder


class FunctionModelBuilder(BaseModelBuilder):
    def __init__(self, id: str, function_name: str, parent_id: str) -> None:
        super().__init__(
            id=id,
            block_type=BlockType.FUNCTION,
            parent_id=parent_id,
        )
        self.function_attributes = FunctionSpecificAttributes(
            function_name=function_name,
            docstring=None,
            decorators=None,
            parameters=None,
            is_method=False,
            is_async=False,
            returns=None,
        )

    def set_parameters_list(
        self, parameter_list_model: ParameterListModel
    ) -> "FunctionModelBuilder":
        """Adds a parameter to the function model."""
        self.function_attributes.parameters = parameter_list_model
        return self

    def set_decorators(
        self, decorators: list[DecoratorModel] | None
    ) -> "FunctionModelBuilder":
        """Adds decorator to the decorators list in the class model."""
        if decorators:
            self.function_attributes.decorators = decorators
        else:
            self.function_attributes.decorators = None
        return self

    def set_docstring(self, docstring: str | None) -> "FunctionModelBuilder":
        """Sets the docstring."""
        self.function_attributes.docstring = docstring
        return self

    def set_return_annotation(self, return_type: str) -> "FunctionModelBuilder":
        """Sets the return type."""
        self.function_attributes.returns = return_type
        return self

    def set_is_method(self, is_method: bool) -> "FunctionModelBuilder":
        """Sets the is_method attribute in the function model."""
        self.function_attributes.is_method = is_method
        return self

    def set_is_async(self, is_async: bool) -> "FunctionModelBuilder":
        """Sets the is_async attribute in the function model."""
        self.function_attributes.is_async = is_async
        return self

    def _get_function_specific_attributes(self) -> dict[str, Any]:
        """
        Gets the function specific attributes from the builder.
        """
        return self.function_attributes.model_dump()

    def build(self) -> FunctionModel:
        """Builds and returns the function model instance."""
        self.build_and_set_children()
        return FunctionModel(
            **self._get_common_attributes(),
            **self._get_function_specific_attributes(),
        )
