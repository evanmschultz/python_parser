from typing import Any, Callable, Protocol, Union
import libcst as cst
from libcst._nodes.internal import CodegenState

import json
from abc import ABC, abstractmethod

from models.enums import BlockType


# ID Generation Strategy Classes
class IDGenerationStrategy(ABC):
    """Abstract base class for ID generation strategies."""

    @staticmethod
    @abstractmethod
    def generate_id(**kwargs) -> str:
        """Generate an ID based on the given context."""
        pass


class ModuleIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for modules."""

    @staticmethod
    def generate_id(file_path: str) -> str:
        return f"{file_path}__>__MODULE"


class ClassIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for classes."""

    @staticmethod
    def generate_id(parent_id: str, class_name: str) -> str:
        return f"{parent_id}__>__CLASS__{class_name}"


class FunctionIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for functions."""

    @staticmethod
    def generate_id(parent_id: str, function_name: str) -> str:
        return f"{parent_id}__>__FUNCTION__{function_name}"


class StandaloneCodeBlockIDGenerationStrategy(IDGenerationStrategy):
    """ID generation strategy for standalone code blocks."""

    @staticmethod
    def generate_id(parent_id: str) -> str:
        return f"{parent_id}__>__STANDALONE_CODE_BLOCK"


# Node classes with a reference to a builder (Bridge Pattern)
class BaseNode:
    def __init__(self, name, node_type, builder, node_id):
        self.name = name
        self.type = node_type
        self.id = node_id
        self.builder = builder
        self.children = []
        self.comments = []  # Storing comments
        self.params = {}  # Storing parameters

    def add_child(self, child):
        self.children.append(child)
        self.builder.add_information(child.name, child.type)

    def add_comment(self, comment):
        self.comments.append(comment)

    def add_param(self, param_name, param_info):
        self.params[param_name] = param_info

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "children": [child.to_dict() for child in self.children],
            "comments": self.comments,
            "params": self.params,
        }


class ModuleNode(BaseNode):
    pass


class ClassNode(BaseNode):
    pass


class FunctionNode(BaseNode):
    pass


# Builder Classes (Simplified for this example)
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


NodeType = Union[ModuleNode, ClassNode, FunctionNode]


# Factory for creating nodes
class NodeFactory:
    # Strategy map for node creation
    _creation_strategies: dict[str, Callable[..., Any]] = {
        "module": lambda name, parent_id=None: ModuleNode(
            name=name,
            node_type="module",
            builder=ModuleModelBuilder(),
            node_id=ModuleIDGenerationStrategy.generate_id(file_path=name),
        ),
        "class": lambda name, parent_id: ClassNode(
            name=name,
            node_type="class",
            builder=ClassModelBuilder(),
            node_id=ClassIDGenerationStrategy.generate_id(
                parent_id=parent_id, class_name=name
            ),
        ),
        "function": lambda name, parent_id: FunctionNode(
            name=name,
            node_type="function",
            builder=FunctionModelBuilder(),
            node_id=FunctionIDGenerationStrategy.generate_id(
                parent_id=parent_id, function_name=name
            ),
        ),
    }

    @staticmethod
    def create_node(node_type, name, parent_id=None) -> NodeType:
        if node_type not in NodeFactory._creation_strategies:
            raise ValueError(f"Unknown node type: {node_type}")
        return NodeFactory._creation_strategies[node_type](name, parent_id=parent_id)


# Base Visitor
class BaseVisitor(cst.CSTVisitor):
    def __init__(self, file_path: str, id: str):
        self.file_path: str = file_path
        self.id: str = id
        self.stack = [NodeFactory.create_node("module", file_path)]

    def extract_code_content(
        self,
        node: cst.CSTNode,
    ) -> str:
        state = CodegenState(default_indent="    ", default_newline="\n")
        node._codegen(state=state)

        return "".join(state.tokens)


# ModuleVisitor
class ModuleVisitor(BaseVisitor):
    def visit_ClassDef(self, node: cst.ClassDef):
        class_node = NodeFactory.create_node(
            "class", node.name.value, parent_id=self.stack[-1].id
        )
        self.stack[-1].add_child(class_node)
        self.stack.append(class_node)

    def leave_ClassDef(self, original_node: cst.ClassDef):
        self.stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef):
        func_node = NodeFactory.create_node(
            "function", node.name.value, parent_id=self.stack[-1].id
        )
        self.stack[-1].add_child(func_node)
        self.stack.append(func_node)

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        self.stack.pop()

    def visit_Comment(self, node: cst.Comment):
        parent_node = self.stack[-1]
        content = self.extract_code_content(node)
        parent_node.add_comment(content)

    def visit_Parameters(self, node: cst.Param):
        parent_node = self.stack[-1]
        param_info = self.extract_code_content(node)
        parent_node.add_param("parameters", param_info)


# Parse and Print Hierarchy Function
def parse_and_print_hierarchy(file_path, code):
    tree = cst.parse_module(code)
    module_id: str = ModuleIDGenerationStrategy.generate_id(file_path=file_path)
    visitor = ModuleVisitor(file_path=file_path, id=module_id)
    tree.visit(visitor)
    hierarchy = visitor.stack[0]
    print(json.dumps(hierarchy.to_dict(), indent=4))


# Example usage
code = """
class MyClass:
    def method1(self):
        pass

    class NestedClass:
        def nested_method(self):
            # This is a comment
            ...
            
class MyClass2:
    def method2(self, param1, param2: int, param3: str = "default"):
        pass
"""

parse_and_print_hierarchy("./", code)
