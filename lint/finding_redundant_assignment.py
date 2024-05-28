'''Finds  redundant variable defination (especially those that next to each other ) 
    in a file and report 
    example:
        x = 5
        x = 4
    '''

import ast
from collections import namedtuple
import sys


#represents a scope on the call stack indicating the name of the scope
Scope = namedtuple("Scope", ["name", "store"])


class FindRedundantAssignment(ast.NodeVisitor):
    '''Uses the visitor pattern to traverse the tree to 
        find all variable assignments in the given scope and
        checks if there is a immediate varibale reassignment then reports it
    '''

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
        if isinstance(node.ctx, ast.Store) and node.id in self.stack[-1].store \
            and self.stack[-1].store[node.id] - node.lineno < 3:

            raise ValueError('Redundant assignment of variable:' 
                             f'{node.id} at line {node.lineno} \
                                and {self.stack[-1].store[node.id]}')
        
        elif isinstance(node.ctx, ast.Store):
            self.stack[-1].store[node.id] = node.lineno
        self.generic_visit(node)

    
if __name__ == '__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader .read()
    tree = ast.parse(source)
    finder = FindRedundantAssignment()
    finder.visit(tree)
