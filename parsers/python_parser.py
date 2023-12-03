import libcst
from libcst.metadata import MetadataWrapper
from id_generation.id_generation_strategies import ModuleIDGenerationStrategy
from model_builders.builder_factory import BuilderFactory
from model_builders.module_model_builder import ModuleModelBuilder

from models.models import ModuleModel
from visitors.module_visitor import ModuleVisitor
from visitors.node_processing.common_functions import get_node_id
from visitors.visitor_manager import VisitorManager
from models.enums import BlockType


class PythonParser:
    """
    A class that represents a Python parser.

    Attributes:
        file_path (str): The path to the Python file to be parsed.

    Example:
        parser = PythonParser("./sample_file.py")
        code: str = parser.open_file()
        module_model: ModuleModel | None = parser.parse(code)
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def open_file(self) -> str:
        """Opens and reads the file specified by the file path and returns the code as a string."""
        with open(self.file_path, "r") as file:
            return file.read()

    def parse(self, code: str) -> ModuleModel | None:
        """
        Parses the given Python code and returns a module model.

        Args:
            code (str): The Python code to be parsed.

        Returns:
            ModuleModel | None: The generated module model if parsing is successful,
            otherwise None.
        """
        wrapper = MetadataWrapper(libcst.parse_module(code))
        module_id: str = ModuleIDGenerationStrategy.generate_id(
            file_path=self.file_path
        )
        module_builder: ModuleModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.MODULE, file_path=self.file_path
        )

        visitor = ModuleVisitor(id=module_id, module_builder=module_builder)
        wrapper.visit(visitor)
        module_model: ModuleModel = self.build_module_model(visitor)

        return module_model if isinstance(module_model, ModuleModel) else None

    def build_module_model(self, visitor: ModuleVisitor) -> ModuleModel:
        """Builds and returns the module model from the given hierarchy."""
        hierarchy: ModuleModelBuilder = visitor.builder_stack[0]  # type: ignore
        return hierarchy.build()
