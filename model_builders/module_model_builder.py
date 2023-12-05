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
    def __init__(self, id: str, file_path: str) -> None:
        super().__init__(id=id, block_type=BlockType.MODULE, parent_id=None)

        self.module_attributes = ModuleSpecificAttributes(
            file_path=file_path,
            docstring=None,
            header=None,
            footer=None,
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
        """Add an import to the dependencies list."""
        if not self.common_attributes.dependencies:
            self.common_attributes.dependencies = []
        self.common_attributes.dependencies.append(import_model)
        return self

    def _get_module_specific_attributes(self) -> dict[str, Any]:
        """Get the module specific attributes."""
        return self.module_attributes.model_dump()

    @logging_decorator(message="Building module model")
    def build(self) -> ModuleModel:
        """Builds and returns the module model instance."""
        self.build_and_set_children()
        return ModuleModel(
            **self._get_common_attributes(), **self._get_module_specific_attributes()
        )
