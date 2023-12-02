from typing import Union

import libcst

from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
    ModuleIDGenerationStrategy,
)
from model_builders.builder_factory import BuilderFactory
from model_builders.class_model_builder import ClassModelBuilder
from model_builders.function_model_builder import FunctionModelBuilder
from model_builders.module_model_builder import ModuleModelBuilder

from models.enums import BlockType
from models.models import CommentModel, DecoratorModel
from visitors.node_processing.common_functions import (
    extract_code_content,
    extract_important_comment,
)


BuilderType = Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder]


class BaseVisitor(libcst.CSTVisitor):
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.builder_stack: list[BuilderType] = []


class ModuleVisitor(BaseVisitor):
    def __init__(self, id: str, module_builder: ModuleModelBuilder) -> None:
        super().__init__(id)
        self.module_builder: ModuleModelBuilder = module_builder
        self.builder_stack.append(module_builder)

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        parent_id: str = self.builder_stack[-1].id
        class_id: str = ClassIDGenerationStrategy.generate_id(
            parent_id=parent_id, class_name=node.name.value
        )

        class_builder: ClassModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.CLASS,
            name=node.name.value,
            parent_id=parent_id,
        )

        parent_builder: BuilderType = self.builder_stack[-1]
        parent_builder.add_child(class_builder)
        self.builder_stack.append(class_builder)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        self.builder_stack.pop()

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        parent_id: str = self.builder_stack[-1].id
        function_id: str = FunctionIDGenerationStrategy.generate_id(
            parent_id=parent_id, function_name=node.name.value
        )

        func_builder: FunctionModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.FUNCTION,
            name=node.name.value,
            parent_id=parent_id,
        )

        parent_builder: BuilderType = self.builder_stack[-1]
        parent_builder.add_child(func_builder)
        self.builder_stack.append(func_builder)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        self.builder_stack.pop()

    def visit_Comment(self, node: libcst.Comment) -> None:
        parent_builder = self.builder_stack[-1]
        content: CommentModel | None = extract_important_comment(node)
        if content:
            parent_builder.add_important_comment(content)

    def visit_Decorator(self, node: libcst.Decorator) -> bool | None:
        parent_builder = self.builder_stack[-1]
        if (
            type(parent_builder) == FunctionModelBuilder
            or type(parent_builder) == ClassModelBuilder
        ):
            decorator: DecoratorModel = DecoratorModel(
                content=extract_code_content(node)
            )
            parent_builder.add_decorator(decorator)
        return True


def parse_and_print_hierarchy(file_path, code) -> None:
    tree: libcst.Module = libcst.parse_module(code)
    module_id: str = ModuleIDGenerationStrategy.generate_id(file_path=file_path)
    module_builder: ModuleModelBuilder = BuilderFactory.create_builder_instance(
        block_type=BlockType.MODULE, file_path=file_path
    )

    module_id: str = module_builder.id
    visitor = ModuleVisitor(id=module_id, module_builder=module_builder)
    tree.visit(visitor)
    hierarchy = visitor.builder_stack[0]
    print(hierarchy.build().model_dump_json(indent=4))


# Example usage
code = """
# NOTE: This is a comment

import os

class MyClass:
    def method1():
        pass
    
    @decorator1
    class NestedClass:
        def nested_method(self, param1, param2: int, param3: str = "default"):
            # NOTE: This is a comment
            ...
@decorator2(arg1, arg2, arg3(arg4, arg5))
@decorator3
def function1():
    pass
"""

parse_and_print_hierarchy("./ex_path", code)
# print(dir(libcst))
