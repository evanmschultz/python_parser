from abc import ABC, abstractmethod
from typing import Any, Callable, Union

import libcst
from libcst._nodes.internal import CodegenState

from id_generation.id_generation_strategies import (
    ClassIDGenerationStrategy,
    FunctionIDGenerationStrategy,
    ModuleIDGenerationStrategy,
)

from models.enums import BlockType, ClassType, MethodType
from models.models import (
    BaseCodeBlockModel,
    ClassKeywordModel,
    ClassModel,
    ClassSpecificAttributes,
    CommentModel,
    DecoratorModel,
    FunctionModel,
    FunctionSpecificAttributes,
    ImportModel,
    ModuleModel,
    ModuleSpecificAttributes,
    ParameterListModel,
)


class BaseModelBuilder(ABC):
    def __init__(
        self, *, id: str, block_type: BlockType, parent_id: str | None
    ) -> None:
        self.id: str = id
        self.children_builders: list[ChildrenBuilderType] = []

        self.common_attributes = BaseCodeBlockModel(
            id=id,
            parent_id=parent_id,
            block_type=block_type,
            block_start_line_number=0,
            block_end_line_number=0,
            code_content="",
            important_comments=None,
            children=[],
            dependencies=None,
            summary=None,
        )

    def add_comment(self, comment):
        if not self.common_attributes.important_comments:
            self.common_attributes.important_comments = []
        self.common_attributes.important_comments.append(comment)

    def set_block_start_line_number(
        self, line_number: int
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the start line number of the code block model instance."""
        self.common_attributes.block_start_line_number = line_number
        return self

    def set_block_end_line_number(
        self, line_number: int
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Sets the end line number of the code block model instance."""
        self.common_attributes.block_end_line_number = line_number
        return self

    def set_code_content(
        self, code_content: str
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds the string containing the content of the code block to the model instance."""
        self.common_attributes.code_content = code_content
        return self

    def set_important_comments(
        self, comment_list: list[CommentModel]
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds an important comment to the model instance."""
        self.common_attributes.important_comments = comment_list
        return self

    def add_summary(
        self, summary
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds a summary to the model instance."""
        return self

    def add_child(
        self, child: Union["ClassModelBuilder", "FunctionModelBuilder"]
    ) -> Union[
        "BaseModelBuilder",
        "ModuleModelBuilder",
        "ClassModelBuilder",
        "FunctionModelBuilder",
    ]:
        """Adds a child code block to the model instance."""
        self.children_builders.append(child)  # type: ignore # TODO: Remove type ignore when stand alone code block model is added
        return self

    def build_and_set_children(self) -> None:
        self.common_attributes.children = [
            child.build() for child in self.children_builders
        ]

    def _get_common_attributes(self) -> dict[str, Any]:
        """
        Returns a dictionary containing the attributes common to all code block models.
        """
        print(self.common_attributes.children)
        return self.common_attributes.model_dump()

    @abstractmethod
    def build(
        self,
    ) -> None:
        """
        Builds and returns the code block model instance.

        Returns:
            CodeBlockModel: The built code block model instance.
        """
        ...


class ModuleModelBuilder(BaseModelBuilder):
    def __init__(self, id: str, file_path: str) -> None:
        super().__init__(id=id, block_type=BlockType.MODULE, parent_id=None)

        self.module_attributes = ModuleSpecificAttributes(
            file_path=file_path,
            docstring=None,
            header=None,
            footer=None,
        )

    def set_docstring(self, docstring: str | None) -> "ModuleModelBuilder":
        """Set the docstring."""
        if docstring:
            self.module_attributes.docstring = docstring
        return self

    def set_header_content(self, header_content: list[str]) -> "ModuleModelBuilder":
        """Set the header."""
        if not self.module_attributes.header:
            self.module_attributes.header = []
        for line in header_content:
            self.module_attributes.header.append(line)
        return self

    def set_footer_content(self, footer_content: list[str]) -> "ModuleModelBuilder":
        """Set the footer."""
        if not self.module_attributes.footer:
            self.module_attributes.footer = []
        for line in footer_content:
            self.module_attributes.footer.append(line)
        return self

    def add_import(self, import_model: ImportModel) -> "ModuleModelBuilder":
        """Add an import to the dependencies list."""
        if not self.common_attributes.dependencies:
            self.common_attributes.dependencies = []
        self.common_attributes.dependencies.append(import_model)
        return self

    def _get_module_specific_attributes(self) -> dict[str, Any]:
        """Get the module specific attributes."""
        return self.module_attributes.model_dump()

    def build(self) -> ModuleModel:
        """Builds and returns the module model instance."""
        self.build_and_set_children()
        return ModuleModel(
            **self._get_common_attributes(), **self._get_module_specific_attributes()
        )


class ClassModelBuilder(BaseModelBuilder):
    def __init__(self, id: str, class_name: str, parent_id: str) -> None:
        super().__init__(id=id, block_type=BlockType.CLASS, parent_id=parent_id)

        self.class_attributes = ClassSpecificAttributes(
            class_name=class_name,
            decorators=None,
            base_classes=None,
            class_type=ClassType.STANDARD,
            docstring=None,
            attributes=None,
            keywords=None,
        )

    def set_decorator_list(
        self, decorator_list: list[DecoratorModel]
    ) -> "ClassModelBuilder":
        """Sets the list of decorators in the function model."""
        self.class_attributes.decorators = decorator_list
        return self

    def set_base_class_list(self, base_classes: list[str]) -> "ClassModelBuilder":
        """Sets the list of base classes to the class model."""
        self.class_attributes.base_classes = base_classes
        return self

    def set_class_type(self, class_type: ClassType) -> "ClassModelBuilder":
        """Sets the type of the class in the model."""
        self.class_attributes.class_type = class_type
        return self

    def set_docstring(self, docstring: str | None) -> "ClassModelBuilder":
        """Sets the docstring of the class in the model."""
        self.class_attributes.docstring = docstring
        return self

    # TODO: Add attribute model
    def add_attribute(self, attribute) -> "ClassModelBuilder":
        """Adds an attribute of the class in the model."""
        if not self.class_attributes.attributes:
            self.class_attributes.attributes = []
        self.class_attributes.attributes.append(attribute)
        return self

    def set_keywords(
        self, keyword_list: list[ClassKeywordModel] | None
    ) -> "ClassModelBuilder":
        """Sets the list of keywords to the class model."""
        self.class_attributes.keywords = keyword_list
        return self

    def _get_class_specific_attributes(self) -> dict[str, Any]:
        """Gets the class specific attributes."""
        return self.class_attributes.model_dump()

    def build(self) -> ClassModel:
        """Creates a ClassModel instance."""
        self.build_and_set_children()
        return ClassModel(
            **self._get_common_attributes(),
            **self._get_class_specific_attributes(),
        )


class FunctionModelBuilder(BaseModelBuilder):
    def __init__(self, id: str, function_name: str, parent_id: str) -> None:
        super().__init__(
            id=id,
            block_type=BlockType.FUNCTION,
            parent_id=parent_id,
        )
        self.function_attributes = FunctionSpecificAttributes(
            function_name=function_name,
            docstring=None,
            decorators=None,
            parameters=None,
            is_method=False,
            method_type=None,
            is_async=False,
            returns=None,
        )

    def set_parameters_list(
        self, parameter_list_model: ParameterListModel
    ) -> "FunctionModelBuilder":
        """Adds a parameter to the function model."""
        self.function_attributes.parameters = parameter_list_model
        return self

    def set_decorator_list(
        self, decorator_list: list[DecoratorModel]
    ) -> "FunctionModelBuilder":
        """Sets the list of decorators in the function model."""
        self.function_attributes.decorators = decorator_list
        return self

    def set_docstring(self, docstring: str | None) -> "FunctionModelBuilder":
        """Sets the docstring."""
        self.function_attributes.docstring = docstring
        return self

    def set_return_annotation(self, return_type: str) -> "FunctionModelBuilder":
        """Sets the return type."""
        self.function_attributes.returns = return_type
        return self

    def set_is_method(self, is_method: bool) -> "FunctionModelBuilder":
        """Sets the is_method attribute in the function model."""
        self.function_attributes.is_method = is_method
        return self

    def set_method_type(self, method_type: MethodType) -> "FunctionModelBuilder":
        ...

    def set_is_async(self, is_async: bool) -> "FunctionModelBuilder":
        """Sets the is_async attribute in the function model."""
        self.function_attributes.is_async = is_async
        return self

    def _get_function_specific_attributes(self) -> dict[str, Any]:
        """
        Gets the function specific attributes from the builder.
        """
        return self.function_attributes.model_dump()

    def build(self) -> FunctionModel:
        """Builds and returns the function model instance."""
        self.build_and_set_children()
        return FunctionModel(
            **self._get_common_attributes(),
            **self._get_function_specific_attributes(),
        )


BuilderType = Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder]
ChildrenBuilderType = Union[ClassModelBuilder, FunctionModelBuilder]


class BuilderFactory:
    _creation_strategies: dict[BlockType, Callable[..., Any]] = {
        BlockType.MODULE: lambda file_path, name=None, parent_id=None: ModuleModelBuilder(
            id=ModuleIDGenerationStrategy.generate_id(file_path=file_path),
            file_path=file_path,
        ),
        BlockType.CLASS: lambda name, parent_id, file_path=None: ClassModelBuilder(
            id=ClassIDGenerationStrategy.generate_id(
                parent_id=parent_id, class_name=name
            ),
            class_name=name,
            parent_id=parent_id,
        ),
        BlockType.FUNCTION: lambda name, parent_id, file_path=None: FunctionModelBuilder(
            id=FunctionIDGenerationStrategy.generate_id(
                parent_id=parent_id, function_name=name
            ),
            function_name=name,
            parent_id=parent_id,
        ),
    }

    @staticmethod
    def create_builder_instance(
        *,
        block_type: BlockType,
        name: str | None = None,
        parent_id: str | None = None,
        file_path: str | None = None,
    ) -> Union[ModuleModelBuilder, ClassModelBuilder, FunctionModelBuilder]:
        if block_type not in BuilderFactory._creation_strategies:
            raise ValueError(f"Unknown node type: {block_type}")
        return BuilderFactory._creation_strategies[block_type](
            name=name, parent_id=parent_id, file_path=file_path
        )


class BaseVisitor(libcst.CSTVisitor):
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.stack: list[BuilderType] = []

    def extract_code_content(
        self,
        node: libcst.CSTNode,
    ) -> str:
        state = CodegenState(default_indent="    ", default_newline="\n")
        node._codegen(state=state)

        return "".join(state.tokens)


class ModuleVisitor(BaseVisitor):
    def __init__(self, id: str, module_builder: ModuleModelBuilder) -> None:
        super().__init__(id)
        self.module_builder: ModuleModelBuilder = module_builder
        self.stack.append(module_builder)

    def visit_ClassDef(self, node: libcst.ClassDef) -> None:
        class_builder: ClassModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.CLASS,
            name=node.name.value,
            parent_id=self.stack[-1].id,
        )  # type: ignore
        parent_builder: BuilderType = self.stack[-1]
        parent_builder.add_child(class_builder)
        self.stack.append(class_builder)

    def leave_ClassDef(self, original_node: libcst.ClassDef) -> None:
        self.stack.pop()

    def visit_FunctionDef(self, node: libcst.FunctionDef) -> None:
        func_builder: FunctionModelBuilder = BuilderFactory.create_builder_instance(
            block_type=BlockType.FUNCTION,
            name=node.name.value,
            parent_id=self.stack[-1].id,
        )  # type: ignore
        parent_builder: BuilderType = self.stack[-1]
        parent_builder.add_child(func_builder)
        self.stack.append(func_builder)

    def leave_FunctionDef(self, original_node: libcst.FunctionDef) -> None:
        self.stack.pop()

    # def visit_Comment(self, node: libcst.Comment) -> None:
    #     parent_node = self.stack[-1]
    #     content: str = self.extract_code_content(node)
    #     parent_node.add_comment(content)


# Parse and Print Hierarchy Function
def parse_and_print_hierarchy(file_path, code) -> None:
    tree: libcst.Module = libcst.parse_module(code)
    module_builder: ModuleModelBuilder = BuilderFactory.create_builder_instance(
        block_type=BlockType.MODULE, file_path=file_path
    )  # type: ignore

    module_id: str = module_builder.id
    visitor = ModuleVisitor(id=module_id, module_builder=module_builder)
    tree.visit(visitor)
    hierarchy = visitor.stack[0]  # NOTE: This is the stack referred to in the TODO
    print(print(hierarchy.build().model_dump_json(indent=4)))


# Example usage
code = """
class MyClass:
    def method1():
        pass

    class NestedClass:
        def nested_method(self, param1, param2: int, param3: str = "default"):
            # This is a comment
            ...
            
def function1():
    pass
"""

parse_and_print_hierarchy("./ex_path", code)
