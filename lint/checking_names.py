
'''Checks if class, functions and variable names follow naming conventions below:
    class should be defined only with camel case
        example:
            class MyClass
    while functions and variables should be defined only with  snake case
        example:
            def my_function

'''


import ast
import sys
import re


CAMEL_CASE = re.compile(r'^[A-Z][a-zA-Z]*$')
SNAKE_CASE = re.compile(r'^[a-z_][a-z0-9_]*$')



class CheckCase(ast.NodeVisitor):
    '''Uses the NodeVisitor from the ast to traverse the tree and find class,
    function and variable defination and performs the check for conformity
    '''

    def visit_ClassDef(self, node):
        self._check(node, 'class', 'camel', node.id)

    def visit_FunctionDef(self, node):
        self._check(node, 'function', 'snake', node.id)

    def visit_Name(self, node):
        self._check(node, 'variable', 'snake', node.id)

    def _check(self, node, node_type, case_type, name):
        if not self.check_case(case_type, name):
            self.report(node_type, node)
        self.generic_visit(node)

    def report(self, type, node):
        name = getattr(node, 'name', None) or getattr(node, 'id', None)
        print(f'The {type}: {name} at line {node.lineno} does not follow naming conventions')

    def check_case(self, case_type, name):
        if case_type == 'camel':
            return bool(CAMEL_CASE.match(name))
        elif case_type == 'snake':
            return bool(SNAKE_CASE.match(name))
        
        assert False, 'Unknown case'
        

if __name__ =='__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader.read()
    tree = ast.parse(source)
    finder = CheckCase()
    finder.visit(tree)
