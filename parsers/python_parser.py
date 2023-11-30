import libcst
from libcst.metadata import MetadataWrapper

from models.models import ModuleModel
from visitors.module_visitor import ModuleVisitor
from visitors.node_processing.common_functions import get_node_id
from visitors.visitor_manager import VisitorManager
from models.enums import BlockType


class PythonParser:
    """
    A class that represents a Python parser meant to parse a python file.

    Attributes:
        file_path (str): The path to the Python file to be parsed.
        visitor_manager (VisitorManager): The visitor manager instance.
        module_id (str): The ID of the module.
        module_visitor (ModuleVisitor): The module visitor instance.
        metadata_repository (MetadataRepository): The metadata repository instance.

    Methods:
        parse(): Parses the content of a file and returns a ModuleModel object representing the parsed module.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.visitor_manager: VisitorManager = VisitorManager.get_instance()

        module_id_context: dict[str, str] = {
            "file_path": self.file_path,
        }
        self.module_id: str = get_node_id(
            node_type=BlockType.MODULE, context=module_id_context
        )

        self.module_visitor = ModuleVisitor(
            file_path=file_path,
            visitor_manager=self.visitor_manager,
            model_id=self.module_id,
        )

    def parse(self) -> ModuleModel | None:
        """
        Parses the content of a file and returns a ModuleModel object representing the parsed module.

        Returns:
            ModuleModel | None: The parsed module as a ModuleModel object, or None if parsing fails.
        """
        with open(self.file_path, "r") as file:
            content: str = file.read()

        # Parse the content and visit using ModuleVisitor
        libcst_tree = libcst.parse_module(content)

        # Wrap the tree with MetadataWrapper for metadata support
        wrapped_tree = MetadataWrapper(libcst_tree)

        # Visit the tree using ModuleVisitor
        wrapped_tree.visit(self.module_visitor)

        # Build and return the ModuleModel
        module_model: ModuleModel = self.module_visitor.model_builder.build()  # type: ignore

        return module_model if isinstance(module_model, ModuleModel) else None
