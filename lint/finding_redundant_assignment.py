'''Docstring.'''

import ast
from collections import namedtuple
import sys


# I would add a comment here to explain what Scope is for.  (It's a
# shame Python doesn't let us attach docstrings to variable
# declarations.)
Scope = namedtuple("Scope", ["name", "store"])


class FindUnusedVariables(ast.NodeVisitor):
    '''Docstring.'''

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
        # why `dict()` rather than `{}` ?
        self.stack.append(Scope(name, dict()))
        self.generic_visit(node)
        self.stack.pop()
    
    def visit_Name(self, node):
        # Wow, this is a long line. I would either split it across
        # multiple lines or (more likely) move it into a helper method
        # with a meaningful name. The same is true of the error
        # message inside the ValueError: it's all useful information,
        # but lines this long are hard to read. You can wrap it by
        # writing several strings on adjacent lines with no commas
        # between them:
        # >>> x = ('first'
        # ... 'second'
        # ... 'third')
        # >>> x
        # 'firstsecondthird'
        if isinstance(node.ctx, ast.Store) and node.id in self.stack[-1].store and self.stack[-1].store[node.id] - node.lineno < 3:
            raise ValueError(f'Redundant assignment of variable: {node.id} at line {node.lineno} and {self.stack[-1].store[node.id]}')
        elif isinstance(node.ctx, ast.Store):
            self.stack[-1].store[node.id] = node.lineno
        self.generic_visit(node)

    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader .read()
    tree = ast.parse(source)
    finder = FindUnusedVariables()
    finder.visit(tree)
