from abc import ABC, abstractmethod
import json
from typing import Any, Callable, Union

import libcst
from libcst._nodes.internal import CodegenState

from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
    ModuleIDGenerationStrategy,
)

from models.enums import BlockType


class BaseModelBuilder:
    def add_information(self, name, node_type):
        pass

    def build(self):
        return {}


class ClassModelBuilder(BaseModelBuilder):
    pass


class FunctionModelBuilder(BaseModelBuilder):
    pass


class ModuleModelBuilder(BaseModelBuilder):
    pass


ModelBuilderType = Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder]


class BaseBridge(ABC):
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.children: list[BridgeType] = []
        self.comments: list[str] = []

        self.block_type: BlockType
        self.builder: ModelBuilderType

    def add_child(self, child) -> None:
        self.children.append(child)

    def add_comment(self, comment):
        self.comments.append(comment)

    @abstractmethod
    def call_build_model(self) -> dict[str, str | list | dict]:
        ...


class ModuleBridge(BaseBridge):
    def __init__(self, id: str) -> None:
        super().__init__(id)

        self.block_type = BlockType.MODULE
        self.builder = ModuleModelBuilder()

    def call_build_model(self) -> dict[str, str | list | dict]:
        return {
            "id": self.id,
            "block_type": self.block_type.name,
            "children": [child.call_build_model() for child in self.children],
            "comments": self.comments,
        }


class ClassBridge(BaseBridge):
    def __init__(self, id: str, class_name: str) -> None:
        super().__init__(id)

        self.class_name: str = class_name
        self.block_type = BlockType.CLASS
        self.builder = ClassModelBuilder()

    def call_build_model(self) -> dict[str, str | list | dict]:
        return {
            "id": self.id,
            "class_name": self.class_name,
            "block_type": self.block_type.name,
            "children": [child.call_build_model() for child in self.children],
            "comments": self.comments,
        }


class FunctionBridge(BaseBridge):
    def __init__(self, id: str, function_name: str) -> None:
        super().__init__(id)

        self.function_name: str = function_name
        self.params: dict[str, str] = {}
        self.block_type = BlockType.FUNCTION
        self.builder = FunctionModelBuilder()

    def add_param(self, param_name, param_info) -> None:
        self.params[param_name] = param_info

    def call_build_model(self) -> dict[str, str | list | dict]:
        return {
            "id": self.id,
            "function_name": self.function_name,
            "block_type": self.block_type.name,
            "children": [child.call_build_model() for child in self.children],
            "comments": self.comments,
            "params": self.params,
        }


BridgeType = Union[ModuleBridge, ClassBridge, FunctionBridge]


class BridgeFactory:
    _creation_strategies: dict[BlockType, Callable[..., Any]] = {
        BlockType.MODULE: lambda file_path, name=None, parent_id=None: ModuleBridge(
            id=ModuleIDGenerationStrategy.generate_id(file_path=file_path),
        ),
        BlockType.CLASS: lambda name, parent_id, file_path=None: ClassBridge(
            class_name=name,
            id=ClassIDGenerationStrategy.generate_id(
                parent_id=parent_id, class_name=name
            ),
        ),
        BlockType.FUNCTION: lambda name, parent_id, file_path=None: FunctionBridge(
            function_name=name,
            id=FunctionIDGenerationStrategy.generate_id(
                parent_id=parent_id, function_name=name
            ),
        ),
    }

    @staticmethod
    def create_bridge_instance(
        *,
        block_type: BlockType,
        name: str | None = None,
        parent_id: str | None = None,
        file_path: str | None = None,
    ) -> Union[ModuleBridge, ClassBridge, FunctionBridge]:
        if block_type not in BridgeFactory._creation_strategies:
            raise ValueError(f"Unknown node type: {block_type}")
        return BridgeFactory._creation_strategies[block_type](
            name=name, parent_id=parent_id, file_path=file_path
        )


class BaseVisitor(libcst.CSTVisitor):
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.stack: list[BridgeType] = []

    def extract_code_content(
        self,
        node: libcst.CSTNode,
    ) -> str:
        state = CodegenState(default_indent="    ", default_newline="\n")
        node._codegen(state=state)

        return "".join(state.tokens)


class ModuleVisitor(BaseVisitor):
    def __init__(self, id: str, module_bridge: ModuleBridge) -> None:
        super().__init__(id)
        self.module_bridge: ModuleBridge = module_bridge
        self.stack.append(module_bridge)

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        class_bridge: ClassBridge = BridgeFactory.create_bridge_instance(
            block_type=BlockType.CLASS,
            name=node.name.value,
            parent_id=self.stack[-1].id,
        )  # type: ignore
        self.stack[-1].add_child(class_bridge)
        self.stack.append(class_bridge)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        self.stack.pop()

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        func_bridge: FunctionBridge = BridgeFactory.create_bridge_instance(
            block_type=BlockType.FUNCTION,
            name=node.name.value,
            parent_id=self.stack[-1].id,
        )  # type: ignore
        self.stack[-1].add_child(func_bridge)
        self.stack.append(func_bridge)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        self.stack.pop()

    def visit_Comment(self, node: libcst.Comment) -> None:
        parent_node = self.stack[-1]
        content = self.extract_code_content(node)
        parent_node.add_comment(content)

    def visit_Parameters(self, node: libcst.Param) -> None:
        parent_node_bridge = self.stack[-1]

        if isinstance(parent_node_bridge, FunctionBridge):
            param_info: str = self.extract_code_content(node)
            parent_node_bridge.add_param("parameters", param_info)


# Parse and Print Hierarchy Function
def parse_and_print_hierarchy(file_path, code) -> None:
    tree: libcst.Module = libcst.parse_module(code)
    module_bridge: ModuleBridge = BridgeFactory.create_bridge_instance(
        block_type=BlockType.MODULE, file_path=file_path
    )  # type: ignore

    module_id: str = module_bridge.id
    visitor = ModuleVisitor(id=module_id, module_bridge=module_bridge)
    tree.visit(visitor)
    hierarchy = visitor.stack[0]  # NOTE: This is the stack referred to in the TODO
    print(json.dumps(hierarchy.call_build_model(), indent=4))


# Example usage
code = """
class MyClass:
    def method1():
        pass

    class NestedClass:
        def nested_method(self, param1, param2: int, param3: str = "default"):
            # This is a comment
            ...
"""

parse_and_print_hierarchy("./ex_path", code)

# TODO: Implement the list comprehension logic in the base builder class
# TODO: Add BridgeFactory to the project
# TODO: Update the BaseVisitor class to use the BridgeFactory and stack
# TODO: Update the ModuleVisitor class to use the BridgeFactory
# TODO: Update the module visitor to have all the logic from the old visitor classes
# TODO: Update the parser to call the stack
