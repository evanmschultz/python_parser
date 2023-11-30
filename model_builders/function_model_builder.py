# TODO: Add `set_method_type` method.

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
    """
    A builder class for creating instances of FunctionModel. It inherits from BaseModelBuilder
    and adds specific attributes and methods for handling function-related details in code blocks.

    Args:
        parent_id (str | None): ID of the parent code block.
        function_name (str): Name of the function.
        function_id (str): Unique identifier for the function.

    Attributes:
        function_attributes (FunctionSpecificAttributes): Holds specific attributes for the function model.

    Methods:
        set_function_name(function_name: str) -> "FunctionModelBuilder":
            Sets the name of the function in the model instance.

        set_decorator_list(decorator_list: list[DecoratorModel]) -> "FunctionModelBuilder":
            Sets the list of decorators in the function model instance.

        set_docstring(docstring: str | None) -> "FunctionModelBuilder":
            Sets the docstring for the function model instance.

        add_parameters_list(parameter_list_model: ParameterListModel) -> "FunctionModelBuilder":
            Adds parameters to the function model instance.

        set_return_annotation(return_type: str) -> "FunctionModelBuilder":
            Sets the return type annotation for the function model.

        set_is_method(is_method: bool) -> "FunctionModelBuilder":
            Sets whether the function is a method.

        set_method_type(method_type: MethodType) -> "FunctionModelBuilder":
            Sets the method type (e.g., instance, class, static) for the function model.

        set_is_async(is_async: bool) -> "FunctionModelBuilder":
            Sets whether the function is asynchronous.

        _get_function_specific_attributes() -> dict[str, Any]:
            Retrieves function-specific attributes for model construction.

        _create_model_instance() -> FunctionModel:
            Constructs and returns an instance of FunctionModel.
    """

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
        """Sets the function name in the function model."""
        self.function_attributes.function_name = function_name
        return self

    def set_decorator_list(
        self, decorator_list: list[DecoratorModel]
    ) -> "FunctionModelBuilder":
        """Sets the list of decorators in the function model."""
        if not self.function_attributes.decorators:
            self.function_attributes.decorators = decorator_list
        # else:
        #     print(
        #         f"Trying to set decorators again for {self.function_attributes.function_name}"
        #     )
        return self

    def set_docstring(self, docstring: str | None) -> "FunctionModelBuilder":
        """Sets the docstring."""
        if not self.function_attributes.docstring:
            self.function_attributes.docstring = docstring
        # else:
        #     print(
        #         f"Trying to set docstring again for {self.function_attributes.function_name}"
        #     )
        return self

    def add_parameters_list(
        self, parameter_list_model: ParameterListModel
    ) -> "FunctionModelBuilder":
        """Adds a parameter to the function model."""
        if not self.function_attributes.parameters:
            self.function_attributes.parameters = parameter_list_model
        # else:
        #     print(
        #         f"Trying to set parameters again for {self.function_attributes.function_name}"
        #     )
        return self

    def set_return_annotation(self, return_type: str) -> "FunctionModelBuilder":
        """Sets the return type."""
        if not self.function_attributes.returns:
            self.function_attributes.returns = return_type
        # else:
        #     print(
        #         f"Trying to set return type again for {self.function_attributes.function_name}"
        #     )
        return self

    def set_is_method(self, is_method: bool) -> "FunctionModelBuilder":
        """Sets the is_method attribute in the function model."""
        if not self.function_attributes.is_method:
            self.function_attributes.is_method = is_method
        # else:
        #     print(
        #         f"Trying to set is_method again for {self.function_attributes.function_name}"
        #     )
        return self

    def set_method_type(self, method_type: MethodType) -> "FunctionModelBuilder":
        ...

    def set_is_async(self, is_async: bool) -> "FunctionModelBuilder":
        """Sets the is_async attribute in the function model."""
        if not self.function_attributes.is_async:
            self.function_attributes.is_async = is_async
        # else:
        #     print(
        #         f"Trying to set is_async again for {self.function_attributes.function_name}"
        #     )
        return self

    def _get_function_specific_attributes(self) -> dict[str, Any]:
        """
        Gets the function specific attributes from the builder.
        """
        # Using `id(self)` to get a unique identifier for the instance
        # print(
        #     f"FunctionModelBuilder Instance: {self}, ID: {id(self)}, Function Name: {self.function_attributes.function_name}"
        # )

        return self.function_attributes.model_dump()

    def _create_model_instance(self) -> FunctionModel:
        """Creates the function model instance with the common and function specific attributes."""
        # print(
        #     f"FunctionModelBuilder Common Attributes from `_create_model_instance`: {self.common_attributes}"
        # )
        return FunctionModel(
            **self._get_common_attributes(),
            **self._get_function_specific_attributes(),
        )
