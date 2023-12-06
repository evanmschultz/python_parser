import logging
from logging import Logger

from typing import Any, Callable, Literal, overload
from logger.decorators import logging_decorator

from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder
from model_builders.standalone_block_model_builder import StandaloneBlockModelBuilder

from models.enums import BlockType


class BuilderFactory:
    """
    A factory class for creating instances of different types of model builders.

    This class uses a strategy pattern to map each block type to a corresponding builder creation function. Depending on the block type specified, it creates and returns an instance of the appropriate model builder class.

    The factory supports creating builders for modules, classes, functions, and standalone code blocks.

    Attributes:
        _creation_strategies (dict[BlockType, Callable[..., Any]]): A dictionary mapping block types to their corresponding builder creation functions.
    """

    _creation_strategies: dict[BlockType, Callable[..., Any]] = {
        BlockType.MODULE: lambda id, file_path, name, parent_id: ModuleModelBuilder(
            id=id,
            file_path=file_path,
        ),
        BlockType.CLASS: lambda id, name, parent_id, file_path: ClassModelBuilder(
            id=id,
            class_name=name,
            parent_id=parent_id,
        ),
        BlockType.FUNCTION: lambda id, name, parent_id, file_path: FunctionModelBuilder(
            id=id,
            function_name=name,
            parent_id=parent_id,
        ),
        BlockType.STANDALONE_CODE_BLOCK: lambda id, parent_id, name, file_path: StandaloneBlockModelBuilder(
            id=id,
            parent_id=parent_id,
        ),
    }

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.MODULE],
        *,
        id: str,
        file_path: str,
    ) -> ModuleModelBuilder:
        """
        Creates a ModuleModelBuilder instance for building module models.

        Args:
            block_type: Specifies that a ModuleModelBuilder is to be created.
            id (str): The unique identifier for the module model.
            file_path (str): The file path of the module.

        Returns:
            ModuleModelBuilder: An instance of ModuleModelBuilder.
        """
        ...

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.CLASS],
        *,
        id: str,
        name: str,
        parent_id: str,
    ) -> ClassModelBuilder:
        """
        Creates a ClassModelBuilder instance for building class models.

        Args:
            block_type: Specifies that a ClassModelBuilder is to be created.
            id (str): The unique identifier for the class model.
            name (str): The name of the class.
            parent_id (str): The identifier of the parent model.

        Returns:
            ClassModelBuilder: An instance of ClassModelBuilder.
        """
        ...

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.FUNCTION],
        *,
        id: str,
        name: str,
        parent_id: str,
    ) -> FunctionModelBuilder:
        """
        Creates a FunctionModelBuilder instance for building function models.

        Args:
            block_type: Specifies that a FunctionModelBuilder is to be created.
            id (str): The unique identifier for the function model.
            name (str): The name of the function.
            parent_id (str): The identifier of the parent model.

        Returns:
            FunctionModelBuilder: An instance of FunctionModelBuilder.
        """
        ...

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.STANDALONE_CODE_BLOCK],
        *,
        id: str,
        parent_id: str,
    ) -> StandaloneBlockModelBuilder:
        """
        Creates a StandaloneBlockModelBuilder instance for building standalone code block models.

        Args:
            block_type: Specifies that a StandaloneBlockModelBuilder is to be created.
            id (str): The unique identifier for the standalone code block model.
            parent_id (str): The identifier of the parent model.

        Returns:
            StandaloneBlockModelBuilder: An instance of StandaloneBlockModelBuilder.
        """
        ...

    @logging_decorator()
    @staticmethod
    def create_builder_instance(
        block_type: BlockType,
        *,
        id: str,
        name: str | None = None,
        parent_id: str | None = None,
        file_path: str | None = None,
    ) -> (
        ModuleModelBuilder
        | ClassModelBuilder
        | FunctionModelBuilder
        | StandaloneBlockModelBuilder
    ):
        """
        Creates and returns an instance of a model builder based on the specified block type.

        Depending on the block type (module, class, function, standalone code block), it creates an instance of the corresponding model builder class.

        Args:
            block_type (BlockType): The type of code block for which the builder is to be created.
            id (str): The unique identifier for the builder.
            name (str | None): The name of the code block (relevant for class or function blocks).
            parent_id (str | None): The identifier of the parent model (if applicable).
            file_path (str | None): The file path of the module (relevant for module blocks).

        Returns:
            Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder, StandaloneBlockModelBuilder]:
            An instance of the appropriate model builder class.

        Raises:
            ValueError: If an unknown block type is provided.

        Example:
            >>> builder = BuilderFactory.create_builder_instance(
                    block_type=BlockType.CLASS,
                    id='class1',
                    name='MyClass',
                    parent_id='module1'
                )
            # This will create an instance of ClassModelBuilder for a class named 'MyClass'.
        """

        if block_type not in BuilderFactory._creation_strategies:
            raise ValueError(f"Unknown node type: {block_type}")
        return BuilderFactory._creation_strategies[block_type](
            id=id, name=name, parent_id=parent_id, file_path=file_path
        )
