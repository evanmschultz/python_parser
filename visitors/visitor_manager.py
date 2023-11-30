from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
    ModuleIDGenerationStrategy,
)
from models.enums import BlockType
from visitors.node_processing.processing_context import PositionData


class VisitorManager:
    """
    Singleton class that manages the state of node processing across different visitors.

    This class ensures that each node in a codebase is processed only once. It follows the Singleton pattern
    and will raise an exception if an attempt is made to create a second instance.

    Attributes:
        _instance (VisitorManager): A singleton instance of VisitorManager.
        processed_nodes (dict): Dictionary tracking processed nodes, organized by module.

    Methods:
        get_instance: Provides a singleton instance of VisitorManager.
        has_been_processed: Checks if a node has already been processed.
        mark_as_processed: Marks a node as processed.
    """

    _instance = None

    @staticmethod
    def get_instance() -> "VisitorManager":
        """
        Provides a singleton instance of VisitorManager.

        Raises:
            RuntimeError: If an instance of VisitorManager already exists.
        """
        if not VisitorManager._instance:
            VisitorManager._instance = VisitorManager()
        return VisitorManager._instance

    def __init__(self) -> None:
        if VisitorManager._instance:
            raise RuntimeError("VisitorManager instance already exists.")
        self.processed_nodes: dict[str, set[str]] = {}

    def has_been_processed(self, module_id: str, code_content: str) -> bool:
        """
        Checks if a node has already been processed in a given module.

        Args:
            module_id (str): Identifier of the module.
            position_data (str): PositionData instance as a unique identifier of the node.

        Returns:
            bool: True if the node has been processed, False otherwise.
        """
        print(f"Checking if node has been processed: {code_content}")
        if module_id not in self.processed_nodes:
            self.processed_nodes[module_id] = set()

        if code_content in self.processed_nodes[module_id]:
            return True

        self.processed_nodes[module_id].add(code_content)
        return False
