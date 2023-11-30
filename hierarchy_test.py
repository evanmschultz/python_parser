import libcst as cst
import json


class Node:
    def __init__(self, name, node_type):
        self.name = name
        self.type = node_type
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "children": [child.to_dict() for child in self.children],
        }


class HierarchyVisitor(cst.CSTVisitor):
    def __init__(self):
        self.stack = [Node(name="Module", node_type="module")]

    def visit_ClassDef(self, node: cst.ClassDef):
        class_node = Node(name=node.name.value, node_type="class")
        self.stack[-1].add_child(class_node)
        self.stack.append(class_node)

    def leave_ClassDef(self, original_node: cst.ClassDef):
        self.stack.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef):
        func_node = Node(name=node.name.value, node_type="function")
        self.stack[-1].add_child(func_node)
        self.stack.append(func_node)

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        self.stack.pop()

    def get_hierarchy(self):
        return self.stack[0]


def parse_and_print_hierarchy(code):
    tree = cst.parse_module(code)
    visitor = HierarchyVisitor()
    tree.visit(visitor)
    hierarchy = visitor.get_hierarchy()
    print(json.dumps(hierarchy.to_dict(), indent=4))


# Example usage
code = """
class MyClass:
    def method1(self):
        pass

    class NestedClass:
        def nested_method(self):
            def nested_nested_method(self):
                pass
            pass
            
            class NestedNestedClass:
                def nested_nested_method(self):
                    pass
                pass
"""

parse_and_print_hierarchy(code)
