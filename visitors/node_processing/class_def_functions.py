from typing import Callable, Mapping, Sequence
import libcst
from libcst.metadata import CodeRange
from model_builders.class_model_builder import ClassModelBuilder

from models.models import ClassKeywordModel


def get_class_id_context(
    class_name: str,
    parent_id: str,
) -> dict[str, str]:
    return {
        "parent_id": parent_id,
        "class_name": class_name,
    }


def get_class_position_data(
    node_name: str, position_metadata: Mapping[libcst.CSTNode, CodeRange]
) -> dict[str, int] | None:
    position_data: dict[str, int] | None = None

    for item in position_metadata:
        if type(item) is libcst.ClassDef and item.name.value == node_name:
            start_line_number: int = position_metadata[item].start.line
            end_line_number: int = position_metadata[item].end.line

            position_data = {
                "start_line_number": start_line_number,
                "end_line_number": end_line_number,
            }

    if position_data:
        return position_data
    else:
        raise Exception(
            "Class position data not found. Check logic in `get_and_set_class_position_data`!"
        )


def extract_bases_from_class(bases: Sequence[libcst.Arg]) -> list[str] | None:
    bases_list: list[str] = []
    for base in bases:
        if (
            isinstance(base, libcst.Arg)
            and isinstance(base.value, libcst.Name)
            and base.value.value
        ):
            bases_list.append(base.value.value)
    return bases_list if bases_list else None


# ===================================================================================================
# Keyword extraction
# ===================================================================================================

operator_map: dict[type[libcst.CSTNode], str] = {
    libcst.Add: "+",
    libcst.Subtract: "-",
    libcst.Multiply: "*",
    libcst.Divide: "/",
    libcst.Modulo: "%",
    libcst.Power: "**",
    libcst.FloorDivide: "//",
    libcst.BitInvert: "~",
    libcst.BitAnd: "&",
    libcst.BitOr: "|",
    libcst.BitXor: "^",
    libcst.LeftShift: "<<",
    libcst.RightShift: ">>",
    libcst.Equal: "==",
    libcst.NotEqual: "!=",
    libcst.LessThan: "<",
    libcst.GreaterThan: ">",
    libcst.LessThanEqual: "<=",
    libcst.GreaterThanEqual: ">=",
    libcst.And: "and",
    libcst.Or: "or",
    libcst.Not: "not",
    libcst.In: "in",
    libcst.NotIn: "not in",
    libcst.Is: "is",
    libcst.IsNot: "is not",
}

NodeHandler = Callable[[libcst.CSTNode], str]


def process_name(node: libcst.Name) -> str:
    return node.value


def process_number(node: libcst.Integer | libcst.Float) -> str:
    return str(node.value)


def process_simple_string(node: libcst.SimpleString) -> str:
    return '"' + node.value.strip('"') + '"'  # Preserve quotes in strings


def process_arg_node(node: libcst.Arg) -> str:
    arg_value: str = process_arg(node.value)
    if node.keyword is not None:
        return f"{node.keyword.value}={arg_value}"
    return arg_value


def process_call(node: libcst.Call) -> str:
    if isinstance(node.func, libcst.Name):
        func_name = node.func.value
    else:
        func_name: str = process_arg(node.func)
    call_args: list[str] = [process_arg(a) for a in node.args]
    return f"{func_name}({', '.join(call_args)})"


def process_list_or_tuple(node: libcst.List | libcst.Tuple) -> str:
    elements: list[str] = [process_arg(e.value) for e in node.elements]
    return (
        f"[{', '.join(elements)}]"
        if isinstance(node, libcst.List)
        else f"({', '.join(elements)})"
    )


def process_dict(node: libcst.Dict) -> str:
    elements: list[str] = [
        f"{process_arg(e.key)}: {process_arg(e.value)}"
        for e in node.elements
        if isinstance(e, libcst.DictElement)
    ]
    return f"{{{', '.join(elements)}}}"


def operator_to_string(
    operator: libcst.CSTNode,
    operator_map: dict[type[libcst.CSTNode], str] = operator_map,
) -> str:
    """Converts a libcst operator node to a string representation."""
    return operator_map.get(type(operator), "unknown_operator")


def process_binary_operation(binary_op, parent_op=None) -> str:
    left_operand: str = process_arg(binary_op.left)
    right_operand: str = process_arg(binary_op.right)
    operator: str = operator_to_string(binary_op.operator)

    if parent_op and isinstance(binary_op, parent_op):
        return f"{left_operand} {operator} {right_operand}"
    else:
        return f"({left_operand} {operator} {right_operand})"


def process_lambda(lambda_node) -> str:
    params: str = ", ".join([param.name.value for param in lambda_node.params.params])
    body: str = process_arg(lambda_node.body)

    return f"lambda {params}: {body}"


def process_comparison(comp_node) -> str:
    left_operand: str = process_arg(comp_node.left)
    comparisons: list[str] = []
    for comparison in comp_node.comparisons:
        operator: str = operator_to_string(comparison.operator)
        comparator: str = process_arg(comparison.comparator)
        comparisons.append(f"{operator} {comparator}")
    return f"{left_operand} {' '.join(comparisons)}"


def process_unknown(node: libcst.CSTNode) -> str:  # TODO: Improve error handling
    return str(node)


# Node Handler mapping
node_handlers: dict[type[libcst.CSTNode], NodeHandler] = {
    libcst.Name: process_name,
    libcst.Integer: process_number,
    libcst.Float: process_number,
    libcst.SimpleString: process_simple_string,
    libcst.Arg: process_arg_node,
    libcst.Call: process_call,
    libcst.List: process_list_or_tuple,
    libcst.Tuple: process_list_or_tuple,
    libcst.Dict: process_dict,
    libcst.Lambda: process_lambda,
    libcst.Comparison: process_comparison,
    libcst.BinaryOperation: process_binary_operation,
}  # type: ignore


def process_arg(arg: libcst.CSTNode) -> str:
    handler: NodeHandler = node_handlers.get(type(arg), process_unknown)
    return handler(arg)


def extract_class_keywords(
    keywords: Sequence[libcst.Arg],
) -> list[ClassKeywordModel] | None:
    keywords_list: list[ClassKeywordModel] = []

    for keyword_arg in keywords:
        if isinstance(keyword_arg, libcst.Arg):
            keyword: str | None = (
                keyword_arg.keyword.value if keyword_arg.keyword else None
            )
            arg_values: list[str] = (
                [process_arg(keyword_arg.value)] if keyword_arg.value else []
            )

            if keyword and arg_values:
                keywords_list.append(
                    ClassKeywordModel(keyword_name=keyword, args=arg_values)
                )
            else:
                raise Exception(
                    "Keyword or argument value not found for class keyword."
                )
    return keywords_list
