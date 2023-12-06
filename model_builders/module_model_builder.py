from typing import Any
from logger.decorators import logging_decorator
from models.models import (
    ModuleModel,
    ImportModel,
    BlockType,
    ModuleSpecificAttributes,
)
from model_builders.base_model_builder import BaseModelBuilder


class ModuleModelBuilder(BaseModelBuilder):
    """
    A builder class for constructing a model of a Python module.

    This class extends BaseModelBuilder and specializes in building a detailed model of a Python module, capturing various aspects such as the module's docstring, header content, footer content, and imports. It allows for the incremental construction of the module model by adding or setting various components.

    Attributes:
        module_attributes (ModuleSpecificAttributes): An instance containing attributes specific to a module, like file path, docstring, header, footer, and imports.

    Args:
        id (str): The unique identifier for the module model.
        file_path (str): The file path of the module being modeled.

    Example:
        >>> module_builder = ModuleModelBuilder(id='module1', file_path='/path/to/module.py')
        >>> module_builder.set_docstring("This is a docstring").add_import(some_import_model)
        # Configures the module builder with a docstring and an import.
    """

    def __init__(self, id: str, file_path: str) -> None:
        super().__init__(id=id, block_type=BlockType.MODULE, parent_id=None)

        self.module_attributes = ModuleSpecificAttributes(
            file_path=file_path,
            docstring=None,
            header=None,
            footer=None,
            imports=None,
        )

    def set_docstring(self, docstring: str | None) -> "ModuleModelBuilder":
        """Set the docstring."""
        if docstring:
            self.module_attributes.docstring = docstring
        return self

    def set_header_content(self, header_content: list[str]) -> "ModuleModelBuilder":
        """Set the header."""
        if not self.module_attributes.header:
            self.module_attributes.header = []
        for line in header_content:
            self.module_attributes.header.append(line)
        return self

    def set_footer_content(self, footer_content: list[str]) -> "ModuleModelBuilder":
        """Set the footer."""
        if not self.module_attributes.footer:
            self.module_attributes.footer = []
        for line in footer_content:
            self.module_attributes.footer.append(line)
        return self

    def add_import(self, import_model: ImportModel) -> "ModuleModelBuilder":
        """Add an import to the imports list."""
        if not self.module_attributes.imports:
            self.module_attributes.imports = []
        self.module_attributes.imports.append(import_model)
        return self

    def _get_module_specific_attributes(self) -> dict[str, Any]:
        """Get the module specific attributes."""
        return self.module_attributes.model_dump()

    @logging_decorator(message="Building module model")
    def build(self) -> ModuleModel:
        """Builds and returns the module model instance after building and setting the children models."""
        self.build_and_set_children()
        return ModuleModel(
            **self._get_common_attributes(), **self._get_module_specific_attributes()
        )
