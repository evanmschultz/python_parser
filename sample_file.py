"""
Example Docstring

sample_something
    sample_something_else
"""

# This is an example header
# TODO: Sample TODO
something = "something"

from dataclasses import dataclass
import os
from typing import Iterable, List as list, Any, Union
from src2.parser import *

# Global variable
some_variable = "Global Variable"


# Function Definitions
@abs(123, "er\n")
def simple_function(param1: str, param2: int):
    """
    A simple function
    """
    # NOTE: Sample NOTE
    return param1 + str(param2)


# Leading comment
@abs(123, "er\n")
@dataclass
# TODO: Sample TODO
class SampleClass(metaclass=type("MyMeta")):
    """
    A sample class

    Attributes:
        attribute1 (str): Sample attribute
        attribute2 (str): Sample attribute with default value
    """

    class NestedClass:
        ...
        # NOTE: Sample NOTE

    # TODO: Sample TODO
    def __init__(self, attribute1: str, attribute2: str = "default"):
        self.attribute1 = attribute1
        self.attribute2 = attribute2

    def standard_method(self, param1) -> str:
        """
        A sample method

        args:
            param1: Sample parameter

        returns:
            str: Sample return value
        """
        return self.attribute1 + param1

    # Sample class method
    @staticmethod
    def class_method(cls, param1: str) -> "SampleClass":
        # def nested_method():
        #     ...
        #     # NOTE: Sample nested_method

        """
        A sample class method
        """
        return cls(param1)


# Test
something = "something"


class SecondClass2(SampleClass, custom_arg=123):
    ...


# Another function
def another_function(param: list[str], param2: Any = None, *args: str, **kwargs):
    """
    Another simple function
    """
    return param


def process_numbers(
    arg: Union[
        str, list[Union[int, None]], tuple[str]
    ],  # Position-only parameters before '/'
    /,
    param: list[Union[str, None, tuple, set, list[int]]] | None,  # Regular parameters
    param2: Iterable = "something",
    *args: list[Union[str, int, None, set[str]]] | int,  # Variadic arguments
    option1: bool = True,  # Keyword-only parameters after '*args'
    option2: int | None = None,
    float: float = 3.14,
    **kwargs,
) -> list[set[str | int]] | dict[str, Any] | None:
    """docstring"""
    for number in param2:
        # Process number
        pass


if __name__ == "__main__":
    obj = SampleClass("attr1", "attr2")
    result: str = obj.standard_method("param1")
    print(result)


# Test Footer

# Footer again
