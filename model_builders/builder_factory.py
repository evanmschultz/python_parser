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
        ...

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.STANDALONE_CODE_BLOCK],
        *,
        id: str,
        parent_id: str,
    ) -> StandaloneBlockModelBuilder:
        ...

    @logging_decorator(level=logging.DEBUG)
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
        if block_type not in BuilderFactory._creation_strategies:
            raise ValueError(f"Unknown node type: {block_type}")
        return BuilderFactory._creation_strategies[block_type](
            id=id, name=name, parent_id=parent_id, file_path=file_path
        )
