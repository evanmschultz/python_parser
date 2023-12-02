from typing import Any, Callable, Literal, overload

from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
    ModuleIDGenerationStrategy,
)

from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder

from models.enums import BlockType


class BuilderFactory:
    _creation_strategies: dict[BlockType, Callable[..., Any]] = {
        BlockType.MODULE: lambda file_path, name, parent_id: ModuleModelBuilder(
            id=ModuleIDGenerationStrategy.generate_id(file_path=file_path),
            file_path=file_path,
        ),
        BlockType.CLASS: lambda name, parent_id, file_path: ClassModelBuilder(
            id=ClassIDGenerationStrategy.generate_id(
                parent_id=parent_id, class_name=name
            ),
            class_name=name,
            parent_id=parent_id,
        ),
        BlockType.FUNCTION: lambda name, parent_id, file_path: FunctionModelBuilder(
            id=FunctionIDGenerationStrategy.generate_id(
                parent_id=parent_id, function_name=name
            ),
            function_name=name,
            parent_id=parent_id,
        ),
    }

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.MODULE],
        *,
        file_path: str,
    ) -> ModuleModelBuilder:
        ...

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.CLASS],
        *,
        name: str,
        parent_id: str,
    ) -> ClassModelBuilder:
        ...

    @staticmethod
    @overload
    def create_builder_instance(
        block_type: Literal[BlockType.FUNCTION],
        *,
        name: str,
        parent_id: str,
    ) -> FunctionModelBuilder:
        ...

    @staticmethod
    def create_builder_instance(
        block_type: BlockType,
        *,
        name: str | None = None,
        parent_id: str | None = None,
        file_path: str | None = None,
    ) -> ModuleModelBuilder | ClassModelBuilder | FunctionModelBuilder:
        if block_type not in BuilderFactory._creation_strategies:
            raise ValueError(f"Unknown node type: {block_type}")
        return BuilderFactory._creation_strategies[block_type](
            name=name, parent_id=parent_id, file_path=file_path
        )
