from typing import Any
from models.models import (
    DecoratorModel,
    FunctionModel,
    FunctionSpecificAttributes,
    ParameterListModel,
    MethodType,
    BlockType,
)
from model_builders.base_model_builder import BaseModelBuilder


class FunctionModelBuilder(BaseModelBuilder):
    def __init__(self, parent_id: str, function_name: str, function_id: str) -> None:
        super().__init__(
            parent_id=parent_id,
            block_type=BlockType.FUNCTION,
            block_id=function_id,
        )
        self.function_attributes = FunctionSpecificAttributes(
            function_name=function_name,
            docstring=None,
            decorators=None,
            parameters=None,
            is_method=False,
            method_type=None,
            is_async=False,
            returns=None,
        )

    def set_function_name(self, function_name: str) -> "FunctionModelBuilder":
        self.function_attributes.function_name = function_name
        return self

    def add_decorator(self, decorator: DecoratorModel) -> "FunctionModelBuilder":
        """Adds a decorator to the function model."""
        if not self.function_attributes.decorators:
            self.function_attributes.decorators = []
        self.function_attributes.decorators.append(decorator)
        return self

    def set_docstring(self, docstring: str | None) -> "FunctionModelBuilder":
        """Sets the docstring."""
        if docstring:
            self.function_attributes.docstring = docstring
        return self

    def add_parameters_list(
        self, parameter_list_model: ParameterListModel
    ) -> "FunctionModelBuilder":
        """Adds a parameter to the function model."""
        self.function_attributes.parameters = parameter_list_model
        return self

    def set_return_annotation(self, return_type: str) -> "FunctionModelBuilder":
        """Sets the return type."""
        self.function_attributes.returns = return_type
        return self

    def set_is_method(self, is_method) -> "FunctionModelBuilder":
        ...

    def set_method_type(self, method_type) -> "FunctionModelBuilder":
        ...

    def set_is_async(self, is_async: bool) -> "FunctionModelBuilder":
        self.function_attributes.is_async = is_async
        return self

    def _get_function_specific_attributes(self) -> dict[str, Any]:
        """Gets the function specific attributes."""
        return self.function_attributes.model_dump()

    def _create_model_instance(self) -> FunctionModel:
        """Creates the function model instance."""
        return FunctionModel(
            **self._get_common_attributes(),
            **self._get_function_specific_attributes(),
        )
