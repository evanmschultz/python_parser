from abc import ABC, abstractmethod
from models.enums import BlockType


class IDGenerationStrategy(ABC):
    """Abstract base class for ID generation strategies."""

    @staticmethod
    @abstractmethod
    def generate_id(**kwargs) -> str:
        """Generate an ID based on the given context.

        Args:
            context: The context for ID generation.

        Returns:
            str: The generated ID.
        """
        pass


class ModuleIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for modules."""

    @staticmethod
    def generate_id(file_path: str) -> str:
        """Generate an ID based on the given file path.

        Args:
            file_path (str): The file path.

        Returns:
            str: The generated ID.
        """
        return f"{file_path}__>__MODULE"


class ClassIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for classes."""

    @staticmethod
    def generate_id(parent_id: str, class_name: str) -> str:
        """Generate an ID based on the given parent ID and class name.

        Args:
            parent_id (str): The parent ID.
            class_name (str): The class name.

        Returns:
            str: The generated ID.
        """
        return f"{parent_id}__>__CLASS_{class_name}"


class FunctionIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for functions."""

    @staticmethod
    def generate_id(parent_id: str, function_name: str) -> str:
        """Generate an ID based on the given parent ID and function name.

        Args:
            parent_id (str): The parent ID.
            function_name (str): The function name.

        Returns:
            str: The generated ID.
        """
        return f"{parent_id}__>__FUNCTION_{function_name}"


class StandaloneCodeBlockIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for standalone code blocks."""

    @staticmethod
    def generate_id(parent_id: str, count: int) -> str:
        """Generate an ID based on the given parent ID and block type.

        Args:
            parent_id (str): The parent ID.

        Returns:
            str: The generated ID.
        """
        return f"{parent_id}__>__STANDALONE_CODE_BLOCK_{count}"
