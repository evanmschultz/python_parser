from typing import Mapping, Sequence

import libcst
from libcst import CSTNode, EmptyLine, MetadataWrapper
from libcst.metadata import WhitespaceInclusivePositionProvider, CodeRange
from models.enums import ImportModuleType
from models.models import ImportModel, ImportNameModel

from visitors.base_code_block_visitor import BaseCodeBlockVisitor
from model_builders.module_model_builder import ModuleModelBuilder
from visitors.class_def_visitor import ClassDefVisitor
from visitors.function_def_visitor import FunctionDefVisitor
from visitors.visitor_manager import VisitorManager


class ModuleVisitor(BaseCodeBlockVisitor, libcst.CSTVisitor):
    """
    Visitor for processing Module nodes in the AST.

    This visitor processes each Module node and delegates processing of child nodes
    like class definitions to specific visitors.

    Args:
        file_path (str): File path of the module being visited.
        parent_visitor_instance (BaseCodeBlockVisitor): Reference to the parent visitor instance.
    """

    def __init__(
        self,
        file_path: str,
        visitor_manager: VisitorManager,
        model_id: str,
    ) -> None:
        super().__init__(
            model_builder=ModuleModelBuilder(file_path=file_path, module_id=model_id),
            file_path=file_path,
            model_id=model_id,
        )
        self.model_builder: ModuleModelBuilder = self.model_builder
        self.visitor_manager: VisitorManager = visitor_manager
        self.metadata_wrapper: MetadataWrapper | None = None

    def visit_Module(self, node: libcst.Module) -> None:
        if not self.visitor_manager.has_been_processed(self.file_path, self.model_id):
            self.metadata_wrapper = MetadataWrapper(node)
            position_metadata: Mapping[
                CSTNode, CodeRange
            ] = self.metadata_wrapper.resolve(WhitespaceInclusivePositionProvider)

            content: str = node.code
            docstring: str | None = node.get_docstring()
            header_content: list[str] = self.get_header_content(node.header)
            footer_content: list[str] = self.get_footer_content(node.footer)

            (
                self.model_builder.set_header_content(header_content)  # type: ignore
                .set_footer_content(footer_content)
                .set_code_content(content)
                .set_docstring(docstring)  # type: ignore
            )

            for child in node.body:
                if isinstance(child, libcst.ClassDef):
                    class_id: str = ClassDefVisitor.get_class_id(
                        child, self.model_id, self.visitor_manager
                    )

                    if not self.visitor_manager.has_been_processed(
                        self.file_path, class_id
                    ):
                        class_name: str = child.name.value
                        class_visitor = ClassDefVisitor(
                            parent_id=self.model_id,
                            parent_visitor_instance=self,
                            class_name=class_name,
                            class_id=class_id,
                            position_metadata=position_metadata,
                            module_code_content=content,
                        )
                        child.visit(class_visitor)

                if isinstance(child, libcst.FunctionDef):
                    function_id: str = FunctionDefVisitor.get_function_id(
                        child, self.model_id, self.visitor_manager
                    )

                    if not self.visitor_manager.has_been_processed(
                        self.file_path, function_id
                    ):
                        function_name: str = child.name.value
                        class_visitor = FunctionDefVisitor(
                            parent_id=self.model_id,
                            parent_visitor_instance=self,
                            function_name=function_name,
                            function_id=function_id,
                            position_metadata=position_metadata,
                            module_code_content=content,
                        )
                        child.visit(class_visitor)

    def visit_Import(self, node: libcst.Import) -> None:
        ModuleVisitor.process_import(node, self.model_builder)

    def visit_ImportFrom(self, node: libcst.ImportFrom) -> None:
        ModuleVisitor.process_import_from(node, self.model_builder)

    def visit_Comment(self, node: libcst.Comment) -> None:
        ModuleVisitor.process_comment(node, self.model_builder)

    def leave_Module(self, original_node: libcst.Module) -> None:
        for child in self.children:
            self.model_builder.add_child(child)

    @staticmethod
    def get_header_content(header_content: Sequence[EmptyLine]) -> list[str]:
        """Gets the header content and returns it as a list of strings."""
        return [
            header_line.comment.value
            for header_line in header_content
            if header_line.comment
        ]

    @staticmethod
    def get_footer_content(footer_content: Sequence[EmptyLine]) -> list[str]:
        """Gets the footer content and returns it as a list of strings."""
        return [
            footer_line.comment.value
            for footer_line in footer_content
            if footer_line.comment
        ]

    @staticmethod
    def get_import_name(node: libcst.Import) -> str:
        return str(node.names[0].name.value)

    @staticmethod
    def get_as_name(node: libcst.Import) -> str | None:
        if node.names[0].asname:
            return str(node.names[0].asname.name.value)  # type: ignore

    @staticmethod
    def build_import_name_model(node: libcst.Import) -> ImportNameModel:
        import_name: str | None = ModuleVisitor.get_import_name(node)
        as_name: str | None = ModuleVisitor.get_as_name(node)
        return ImportNameModel(name=import_name, as_name=as_name)

    @staticmethod
    def build_import_model(
        import_name_models: list[ImportNameModel],
    ) -> ImportModel:
        return ImportModel(
            import_names=import_name_models,
            imported_from=None,
            import_module_type=ImportModuleType.STANDARD_LIBRARY,  # TODO: Add logic to determine import module type
        )

    @staticmethod
    def process_import(node: libcst.Import, model_builder: ModuleModelBuilder) -> None:
        import_name_model: ImportNameModel = ModuleVisitor.build_import_name_model(node)
        import_model: ImportModel = ModuleVisitor.build_import_model(
            import_name_models=[import_name_model]
        )
        ModuleVisitor.add_import_to_model_builder(import_model, model_builder)

    @staticmethod
    def add_import_to_model_builder(
        import_model: ImportModel, model_builder: ModuleModelBuilder
    ) -> None:
        if isinstance(model_builder, ModuleModelBuilder):
            model_builder.add_import(import_model)

    @staticmethod
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
            return ".".join(
                [ModuleVisitor.get_full_module_path(node.value), node.attr.value]
            )
        else:
            return str(node)

    @staticmethod
    def process_import_from(
        node: libcst.ImportFrom, model_builder: ModuleModelBuilder
    ) -> None:
        module_name: str | None = (
            ModuleVisitor.get_full_module_path(node.module) if node.module else None
        )
        import_names: list[
            ImportNameModel
        ] = ModuleVisitor.build_import_from_name_models(node)

        import_model = ImportModel(
            import_names=import_names,
            imported_from=module_name,
            import_module_type=ImportModuleType.STANDARD_LIBRARY,  # TODO: Add logic to determine import module type
        )

        ModuleVisitor.add_import_to_model_builder(import_model, model_builder)

    @staticmethod
    def extract_as_name(import_alias: libcst.ImportAlias) -> str | None:
        if import_alias.asname and isinstance(import_alias.asname, libcst.AsName):
            if isinstance(import_alias.asname.name, libcst.Name):
                return import_alias.asname.name.value
        return None

    @staticmethod
    def build_import_from_name_models(node: libcst.ImportFrom) -> list[ImportNameModel]:
        import_names: list[ImportNameModel] = []
        if isinstance(node.names, libcst.ImportStar):
            import_names.append(ImportNameModel(name="*", as_name=None))
        else:
            for import_alias in node.names:
                if isinstance(import_alias, libcst.ImportAlias):
                    name = str(import_alias.name.value)
                    as_name = ModuleVisitor.extract_as_name(import_alias)
                    import_names.append(ImportNameModel(name=name, as_name=as_name))
        return import_names
