'''Docstring.'''

import ast
import sys


class CheckDocStrings(ast.NodeVisitor):
    '''Docstring.'''

    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node):
            self.report('function', node)    
        self.generic_visit(node)

    def visit_ClassDef(self,node):
        if not ast.get_docstring(node):
            self.report('class', node)
        self.generic_visit(node)

    # As in checking_names.py, I would write a helper method that
    # `visit_FunctionDef` and `visit_ClassDef` call because their
    # bodies are identical except for the constant strings 'function'
    # and 'class'.
    
    def report(self, node_type, node):
        print(f'{node_type} {node.name} does not have a docstring')


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader .read()
    tree = ast.parse(source)
    finder = CheckDocStrings()
    finder.visit(tree)
