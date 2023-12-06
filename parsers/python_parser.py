import libcst
from libcst.metadata import MetadataWrapper
from id_generation.id_generation_strategies import ModuleIDGenerationStrategy
from model_builders.builder_factory import BuilderFactory
from model_builders.module_model_builder import ModuleModelBuilder

from models.models import ModuleModel
from visitors.module_visitor import ModuleVisitor
from models.enums import BlockType


class PythonParser:
    """
    A parser for Python source code, using libcst to parse and construct a module model.

    This class takes the path to a Python file, reads its contents, and parses it into a structured
    module model using the libcst library. It is designed to work with a specific file at a time.

    Attributes:
        file_path (str): The path to the Python file to be parsed.

    Example:
        >>> python_parser = PythonParser("/path/to/python/file.py")
        >>> module_model = python_parser.parse(python_parser.open_file())
        # This will parse the specified Python file and return a structured module model.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path

    def open_file(self) -> str:
        """
        Opens and reads the contents of the Python file specified in the file_path attribute.

        Returns:
            str: The contents of the file as a string.

        Example:
            >>> code = python_parser.open_file()
            # Reads and returns the contents of the Python file.
        """

        with open(self.file_path, "r") as file:
            return file.read()

    def parse(self, code: str) -> ModuleModel | None:
        """
        Parses the given Python code into a structured module model.

        Uses libcst to parse the code and constructs a module model using a ModuleVisitor and various model builders.

        Args:
            code (str): The Python code to parse.

        Returns:
            ModuleModel | None: A structured module model if parsing is successful, otherwise None.

        Example:
            >>> module_model = python_parser.parse(code)
            # Parses the provided code and returns a module model.
        """

        wrapper = MetadataWrapper(libcst.parse_module(code))
        module_id: str = ModuleIDGenerationStrategy.generate_id(
            file_path=self.file_path
        )
        module_builder: ModuleModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.MODULE, id=module_id, file_path=self.file_path
        )

        visitor = ModuleVisitor(id=module_id, module_builder=module_builder)
        wrapper.visit(visitor)
        module_model: ModuleModel = self.build_module_model(visitor)

        return module_model if isinstance(module_model, ModuleModel) else None

    def build_module_model(self, visitor: ModuleVisitor) -> ModuleModel:
        """
        Builds a module model from the ModuleVisitor's builder stack.

        Extracts the ModuleModelBuilder from the visitor's builder stack and constructs the module model. Assumes that the first element in the builder stack is a ModuleModelBuilder.

        Args:
            visitor (ModuleVisitor): The visitor that has traversed the CST.

        Returns:
            ModuleModel: The constructed module model.

        Example:
            >>> module_model = python_parser.build_module_model(visitor)
            # Builds and returns a module model from the visitor.
        """

        if not isinstance(visitor.builder_stack[0], ModuleModelBuilder):
            raise TypeError("Expected the first builder to be a ModuleModelBuilder")

        hierarchy: ModuleModelBuilder = visitor.builder_stack[0]
        return hierarchy.build()
