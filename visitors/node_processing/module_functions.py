import sys
from typing import Sequence

import libcst
from models.enums import ImportModuleType
from models.models import ImportModel, ImportNameModel


def extract_content_from_empty_lines(
    sequence: Sequence[libcst.EmptyLine],
) -> list[str]:
    """
    Extracts comments from a sequence of EmptyLine nodes.

    Args:
        sequence: A sequence of libcst.EmptyLine nodes to process.

    Returns:
        A list of string comments extracted from the EmptyLine nodes.

    Example:
        >>> extract_content_from_empty_lines([libcst.EmptyLine(comment=libcst.Comment("# Comment"))])
        ['# Comment']
    """

    return [line.comment.value for line in sequence if line.comment]


def process_import(node: libcst.Import) -> ImportModel:
    """
    Processes an Import node to create an ImportModel.

    Args:
        node: The Import node to process.

    Returns:
        An ImportModel representing the processed import.

    Example:
        >>> process_import(libcst.Import(names=[libcst.ImportAlias(name=libcst.Name("module"))]))
        # Returns an ImportModel for 'module'
    """

    import_name_model: ImportNameModel = _build_import_name_model(node)
    import_model: ImportModel = _build_import_model(
        import_name_models=[import_name_model]
    )
    return import_model


def process_import_from(node: libcst.ImportFrom) -> ImportModel:
    """
    Processes an ImportFrom node to create an ImportModel.

    Args:
        node: The ImportFrom node to process.

    Returns:
        An ImportModel representing the processed import from statement.

    Example:
        >>> process_import_from(libcst.ImportFrom(module=libcst.Name("module"), names=[libcst.ImportAlias(name=libcst.Name("submodule"))]))
        # Returns an ImportModel for 'from module import submodule'
    """

    module_name: str | None = (
        _get_full_module_path(node.module) if node.module else None
    )
    import_names: list[ImportNameModel] = _build_import_from_name_models(node)
    import_module_type: ImportModuleType = _get_import_from_module_type(module_name)

    import_model = ImportModel(
        import_names=import_names,
        imported_from=module_name,
        import_module_type=import_module_type,
    )
    return import_model


def _get_import_name(node: libcst.Import) -> str:
    """Gets the import name from an Import node."""

    return str(node.names[0].name.value)


def _get_as_name(node: libcst.Import) -> str | None:
    """Gets the as name from an Import node."""

    first_name: libcst.ImportAlias = node.names[0]

    if first_name.asname and isinstance(first_name.asname, libcst.AsName):
        as_name_node = first_name.asname.name
        if isinstance(as_name_node, libcst.Name):
            return as_name_node.value


def _build_import_name_model(node: libcst.Import) -> ImportNameModel:
    """Builds an ImportNameModel from an Import node."""

    import_name: str | None = _get_import_name(node)
    as_name: str | None = _get_as_name(node)
    return ImportNameModel(name=import_name, as_name=as_name)


def _is_standard_library_import(import_name: str) -> bool:
    """Checks if an import is a standard library import."""

    return import_name in sys.stdlib_module_names


def _third_party_imports() -> list[str]:
    """Gets a list of all third party imports."""

    third_party_imports: list[str] = []

    for module_name, module in sys.modules.items():
        if module_name in sys.stdlib_module_names or not hasattr(module, "__file__"):
            continue

        module_file: str | None = module.__file__
        if module_file and (
            "site-packages" in module_file or "dist-packages" in module_file
        ):
            third_party_imports.append(module_name)

    return third_party_imports


def _is_third_party_import(import_name: str) -> bool:
    """Checks if an import is a third party import."""

    return import_name in _third_party_imports()


def _determine_import_module_type(module_name: str) -> ImportModuleType:
    """Determines the type of import a module is."""

    if _is_standard_library_import(module_name):
        return ImportModuleType.STANDARD_LIBRARY
    elif _is_third_party_import(module_name):
        return ImportModuleType.THIRD_PARTY
    else:
        return ImportModuleType.LOCAL


def _get_import_module_type(
    import_name_models: list[ImportNameModel],
) -> ImportModuleType:
    """Gets the import module type of a list of ImportNameModels."""

    for import_name_model in import_name_models:
        module_type = _determine_import_module_type(import_name_model.name)
        if module_type != ImportModuleType.LOCAL:
            return module_type
    return ImportModuleType.LOCAL


def _get_import_from_module_type(module_name: str | None) -> ImportModuleType:
    """Gets the import module type of an ImportFrom node."""

    if module_name:
        return _determine_import_module_type(module_name)
    return ImportModuleType.LOCAL


def _build_import_model(
    import_name_models: list[ImportNameModel],
) -> ImportModel:
    """Builds an ImportModel from a list of ImportNameModels."""

    import_module_type: ImportModuleType = _get_import_module_type(import_name_models)
    return ImportModel(
        import_names=import_name_models,
        imported_from=None,
        import_module_type=import_module_type,
    )


def _get_full_module_path(node) -> str:
    """Recursively gets the full module path from a node and returns it as a string."""

    if isinstance(node, libcst.Name):
        return node.value
    elif isinstance(node, libcst.Attribute):
        return ".".join([_get_full_module_path(node.value), node.attr.value])
    else:
        return str(node)


def _extract_as_name(import_alias: libcst.ImportAlias) -> str | None:
    """Extracts the as name from an ImportAlias node."""

    if import_alias.asname and isinstance(import_alias.asname, libcst.AsName):
        if isinstance(import_alias.asname.name, libcst.Name):
            return import_alias.asname.name.value


def _build_import_from_name_models(node: libcst.ImportFrom) -> list[ImportNameModel]:
    """Builds a list of ImportNameModels from an ImportFrom node."""

    import_names: list[ImportNameModel] = []
    if isinstance(node.names, libcst.ImportStar):
        import_names.append(ImportNameModel(name="*", as_name=None))
    else:
        for import_alias in node.names:
            if isinstance(import_alias, libcst.ImportAlias):
                name = str(import_alias.name.value)
                as_name = _extract_as_name(import_alias)
                import_names.append(ImportNameModel(name=name, as_name=as_name))
    return import_names
