from abc import ABC, abstractmethod
from models.enums import BlockType


class IDGenerationStrategy(ABC):
    """
    Abstract base class defining the interface for ID generation strategies.

    This class serves as a template for creating various ID generation strategies for different types
    of code blocks, such as modules, classes, functions, and standalone code blocks.
    """

    @staticmethod
    @abstractmethod
    def generate_id(**kwargs) -> str:
        """
        Abstract method to generate an ID based on the given context.

        Subclasses should implement this method to generate an ID specific to the block type.

        Args:
            **kwargs: Variable keyword arguments depending on the specific strategy requirements.

        Returns:
            str: The generated ID.
        """
        pass


class ModuleIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for modules."""

    @staticmethod
    def generate_id(file_path: str) -> str:
        """
        Generates an ID for a module based on the given file path.

        Args:
            file_path (str): The file path of the module.

        Returns:
            str: The generated ID, incorporating the file path.
        """
        return f"{file_path}__>__MODULE"


class ClassIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for classes."""

    @staticmethod
    def generate_id(parent_id: str, class_name: str) -> str:
        """
        Generates an ID for a class based on the given parent ID and class name.

        Args:
            parent_id (str): The ID of the parent (module or another class).
            class_name (str): The name of the class.

        Returns:
            str: The generated ID, incorporating the parent ID and class name.
        """
        return f"{parent_id}__>__CLASS_{class_name}"


class FunctionIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for functions."""

    @staticmethod
    def generate_id(parent_id: str, function_name: str) -> str:
        """
        Generates an ID for a function based on the given parent ID and function name.

        Args:
            parent_id (str): The ID of the parent (module or class).
            function_name (str): The name of the function.

        Returns:
            str: The generated ID, incorporating the parent ID and function name.
        """
        return f"{parent_id}__>__FUNCTION_{function_name}"


class StandaloneCodeBlockIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for standalone code blocks."""

    @staticmethod
    def generate_id(parent_id: str, count: int) -> str:
        """
        Generates an ID for a standalone code block based on the given parent ID and a count.

        Args:
            parent_id (str): The ID of the parent (typically a module).
            count (int): A unique count or index for the standalone block within its parent.

        Returns:
            str: The generated ID, incorporating the parent ID and the count.
        """
        return f"{parent_id}__>__STANDALONE_CODE_BLOCK_{count}"
