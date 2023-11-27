from enum import Enum


class ImportModuleType(Enum):
    """Enum of import module types."""

    STANDARD_LIBRARY = "STANDARD_LIBRARY"
    LOCAL = "LOCAL"  # Local to the codebase itself
    THIRD_PARTY = "THIRD_PARTY"

    def __str__(self) -> str:
        return self.value


class CommentType(Enum):
    """Class representing the different types of important comments."""

    TODO = "TODO"
    FIXME = "FIXME"
    NOTE = "NOTE"
    HACK = "HACK"
    XXX = "XXX"
    REVIEW = "REVIEW"
    OPTIMIZE = "OPTIMIZE"
    CHANGED = "CHANGED"
    QUESTION = "QUESTION"
    Q = "Q"
    DEPRECATED = "@deprecated"
    NOSONAR = "NOSONAR"
    TODO_FIXME = "TODO-FIXME"

    def __str__(self) -> str:
        return self.value


class BlockType(Enum):
    """Enum of code block types."""

    STANDALONE_CODE_BLOCK = "STANDALONE_BLOCK"
    IMPORT_BLOCK = "IMPORT_BLOCK"
    CLASS = "CLASS"
    FUNCTION = "FUNCTION"
    MODULE = "MODULE"  # The module itself, ie. the file

    def __str__(self) -> str:
        return self.value


class MethodType(Enum):
    """Enum of method types."""

    INSTANCE = "INSTANCE"
    CLASS = "CLASS"
    STATIC = "STATIC"
    ASYNC_INSTANCE = "ASYNC_INSTANCE"
    ASYNC_CLASS = "ASYNC_CLASS"
    ASYNC_STATIC = "ASYNC_STATIC"
    ABSTRACT = "ABSTRACT"
    MAGIC = "MAGIC"
    STANDALONE_FUNCTION = "STANDALONE_FUNCTION"

    def __str__(self) -> str:
        return self.value


class ClassType(Enum):
    """Enum of class types."""

    STANDARD = "STANDARD"  # Regular, commonly used classes
    ABSTRACT = "ABSTRACT"  # Abstract classes, typically containing one or more abstract methods
    INTERFACE = "INTERFACE"  # Used for classes that act as interfaces (more conceptual in Python)
    MIXIN = "MIXIN"  # Mixin classes, providing additional functionality for multiple inheritance
    SINGLETON = "SINGLETON"  # Singleton classes, where only one instance should exist
    FACTORY = "FACTORY"  # Factory classes, used for creating instances of other classes
    BUILDER = "BUILDER"  # Builder classes, used for constructing complex objects
    PROTOTYPE = "PROTOTYPE"  # Prototype classes, used for cloning new instances
    ADAPTER = "ADAPTER"  # Adapter classes, used to adapt one interface to another
    DECORATOR = "DECORATOR"  # Decorator classes, used to add responsibilities to objects dynamically
    FACADE = (
        "FACADE"  # Facade classes, providing a simplified interface to a complex system
    )
    PROXY = "PROXY"  # Proxy classes, used to control access to another object
    COMPOSITE = "COMPOSITE"  # Composite classes, used to build a hierarchy of objects
    COMMAND = "COMMAND"  # Command classes, encapsulating a request as an object
    OBSERVER = "OBSERVER"  # Observer classes, used in the observer design pattern
    STRATEGY = (
        "STRATEGY"  # Strategy classes, enabling selection of an algorithm at runtime
    )
    STATE = "STATE"  # State classes, used in the state design pattern
    TEMPLATE = "TEMPLATE"  # Template classes, used in the template method pattern
    VISITOR = "VISITOR"  # Visitor classes, used in the visitor design pattern

    def __str__(self) -> str:
        return self.value
