from typing import Union
from pydantic import BaseModel, Field, validator

from models.enums import (
    BlockType,
    ImportModuleType,
    CommentType,
    MethodType,
    ClassType,
)


class ImportNameModel(BaseModel):
    """Class representing the name of an import."""

    name: str
    as_name: str | None = None


class ImportModel(BaseModel):
    """Class representing an import statement."""

    import_names: list[ImportNameModel]
    imported_from: str | None = None
    import_module_type: ImportModuleType = ImportModuleType.STANDARD_LIBRARY


class CommentModel(BaseModel):
    """Class representing a comment."""

    content: str
    comment_type: CommentType


class DecoratorModel(BaseModel):
    """Class representing a decorator."""

    decorator_name: str
    decorator_args: list[str] | None = None


class ClassKeywordModel(BaseModel):
    """Class representing a class keyword."""

    keyword_name: str
    arg_value: str


class ParameterModel(BaseModel):
    """Class representing a function parameter."""

    content: str


class ParameterListModel(BaseModel):
    """Class representing a list of parameters."""

    params: list[ParameterModel] | None = None
    star_arg: ParameterModel | None = None
    kwonly_params: list[ParameterModel] | None = None
    star_kwarg: ParameterModel | None = None
    posonly_params: list[ParameterModel] | None = None


class BaseCodeBlockModel(BaseModel):
    """Attributes common to all code block models."""

    id: str | None = None
    parent_id: str | None = None
    block_type: BlockType
    block_start_line_number: int
    block_end_line_number: int
    code_content: str
    important_comments: list[CommentModel] | None = None
    dependencies: list[ImportModel] | None = None
    summary: str | None = None
    children: list[
        Union[
            "ClassModel",
            "FunctionModel",
            "StandaloneCodeBlockModel",
        ]
    ] | None = None

    @validator("parent_id", always=True)
    def check_parent_id(cls, v, values, **kwargs) -> str | None:
        """Validates that parent_id is a non-empty string unless block_type is MODULE."""

        if "block_type" in values and values["block_type"] != BlockType.MODULE:
            if len(v) < 1:
                raise ValueError("parent_id is required!")
        return v


class ModuleSpecificAttributes(BaseModel):
    """Module specific attributes."""

    file_path: str = Field(min_length=1)
    docstring: str | None = None
    header: list[str] | None = None
    footer: list[str] | None = None


class ModuleModel(BaseCodeBlockModel, ModuleSpecificAttributes):
    """Model for a module."""

    ...


class ClassSpecificAttributes(BaseModel):
    """Class specific attributes."""

    class_name: str = Field(min_length=1)
    decorators: list[DecoratorModel] | None = None
    base_classes: list[str] | None = None
    class_type: ClassType
    docstring: str | None = None
    attributes: list[dict] | None = None
    keywords: list[ClassKeywordModel] | None = None
    # type_parameters: list[str] | None = None # TODO: Add logic if proves useful


class ClassModel(BaseCodeBlockModel, ClassSpecificAttributes):
    """Model for a class."""

    ...


class FunctionSpecificAttributes(BaseModel):
    """Function specific attributes."""

    function_name: str = Field(min_length=1)
    docstring: str | None = None
    decorators: list[DecoratorModel] | None = None
    parameters: ParameterListModel | None = None
    returns: str | None = None
    is_method: bool = False
    method_type: MethodType | None = None
    is_async: bool = False
    # type_parameters: list[str] | None = None # TODO: Add logic if proves useful


class FunctionModel(BaseCodeBlockModel, FunctionSpecificAttributes):
    """Model for a function."""

    ...


class StandaloneCodeBlockModel(BaseCodeBlockModel):
    """Model for a standalone code block."""

    ...
