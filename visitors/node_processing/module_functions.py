from typing import Sequence

import libcst
from models.enums import ImportModuleType

from model_builders.module_model_builder import ModuleModelBuilder
from models.models import ImportModel, ImportNameModel


def get_header_content(header_content: Sequence[libcst.EmptyLine]) -> list[str]:
    """Gets the header content and returns it as a list of strings."""
    return [
        header_line.comment.value
        for header_line in header_content
        if header_line.comment
    ]


def get_footer_content(footer_content: Sequence[libcst.EmptyLine]) -> list[str]:
    """Gets the footer content and returns it as a list of strings."""
    return [
        footer_line.comment.value
        for footer_line in footer_content
        if footer_line.comment
    ]


def get_import_name(node: libcst.Import) -> str:
    return str(node.names[0].name.value)


def get_as_name(node: libcst.Import) -> str | None:
    if node.names[0].asname:
        return str(node.names[0].asname.name.value)  # type: ignore


@staticmethod
def build_import_name_model(node: libcst.Import) -> ImportNameModel:
    import_name: str | None = get_import_name(node)
    as_name: str | None = get_as_name(node)
    return ImportNameModel(name=import_name, as_name=as_name)


def build_import_model(
    import_name_models: list[ImportNameModel],
) -> ImportModel:
    return ImportModel(
        import_names=import_name_models,
        imported_from=None,
        import_module_type=ImportModuleType.STANDARD_LIBRARY,  # TODO: Add logic to determine import module type
    )


def process_import(node: libcst.Import, model_builder: ModuleModelBuilder) -> None:
    import_name_model: ImportNameModel = build_import_name_model(node)
    import_model: ImportModel = build_import_model(
        import_name_models=[import_name_model]
    )
    add_import_to_model_builder(import_model, model_builder)


def add_import_to_model_builder(
    import_model: ImportModel, model_builder: ModuleModelBuilder
) -> None:
    if isinstance(model_builder, ModuleModelBuilder):
        model_builder.add_import(import_model)


def get_full_module_path(node) -> str:
    """
    Returns the full path string representation of a given import.

    Args:
        node: The node to get the full path string for.

    Returns:
        The full path string representation of the import.
    """
    if isinstance(node, libcst.Name):
        return node.value
    elif isinstance(node, libcst.Attribute):
        return ".".join([get_full_module_path(node.value), node.attr.value])
    else:
        return str(node)


def process_import_from(
    node: libcst.ImportFrom, model_builder: ModuleModelBuilder
) -> None:
    module_name: str | None = get_full_module_path(node.module) if node.module else None
    import_names: list[ImportNameModel] = build_import_from_name_models(node)

    import_model = ImportModel(
        import_names=import_names,
        imported_from=module_name,
        import_module_type=ImportModuleType.STANDARD_LIBRARY,  # TODO: Add logic to determine import module type
    )

    add_import_to_model_builder(import_model, model_builder)


def extract_as_name(import_alias: libcst.ImportAlias) -> str | None:
    if import_alias.asname and isinstance(import_alias.asname, libcst.AsName):
        if isinstance(import_alias.asname.name, libcst.Name):
            return import_alias.asname.name.value
    return None


def build_import_from_name_models(node: libcst.ImportFrom) -> list[ImportNameModel]:
    import_names: list[ImportNameModel] = []
    if isinstance(node.names, libcst.ImportStar):
        import_names.append(ImportNameModel(name="*", as_name=None))
    else:
        for import_alias in node.names:
            if isinstance(import_alias, libcst.ImportAlias):
                name = str(import_alias.name.value)
                as_name = extract_as_name(import_alias)
                import_names.append(ImportNameModel(name=name, as_name=as_name))
    return import_names
