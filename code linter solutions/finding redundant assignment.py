import ast
from collections import namedtuple
import sys

Scope = namedtuple("Scope",["name", "store"])

class FindUnusedVariables(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.stack = []
    
    def visit_Module(self, node):
        self.search("global", node)
        
    def visit_FunctionDef(self, node):
        self.search(node.name, node)

    def visit_ClassDef(self, node):
        self.search(node.name, node)


    def search(self, name, node):
        self.stack.append(Scope(name, dict()))
        self.generic_visit(node)
        self.stack.pop()
    

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) and node.id in self.stack[-1].store:
            if self.stack[-1].store[node.id] - node.lineno < 3:
                raise ValueError(f'Redundant assignment of varibale: {node.id} at line {node.lineno} and {self.stack[-1].store[node.id]}')
        elif isinstance(node.ctx, ast.Store):
            self.stack[-1].store[node.id] = node.lineno
        self.generic_visit(node)

    

with open(sys.argv[1], 'r') as reader:
    source = reader .read()
tree = ast.parse(source)
# print(ast.dump(tree, indent=4))
finder = FindUnusedVariables()
finder.visit(tree)
