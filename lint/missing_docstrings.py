'''Finds and  reports class and functions without docstrings'''


import ast
import sys


class CheckDocStrings(ast.NodeVisitor):
    '''Uses the ast.NodeVisitor to traverse the AST of the code and locate class and function defination'''

    def visit_FunctionDef(self, node):
        self._check_docstring('function', node)

    def visit_ClassDef(self,node):
        self.check_docstring('class', node)        

    
    def _check_docstring(self, node_type, node):
        if not ast.get_docstring(node):
            self.report(node_type, node)
        self.generic_visit(node)
    
    def report(self, node_type, node):
        print(f'{node_type} {node.name} does not have a docstring')


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader .read()
    tree = ast.parse(source)
    finder = CheckDocStrings()
    finder.visit(tree)
