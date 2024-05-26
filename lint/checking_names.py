'''I like to put a docstring at the top of the file.

It's good practice for larger projects, and reminds me what I was
doing when I come back to the code later.

I have also added double blank lines between the imports, the
constants, the class definition, and the __main__ runner. You might
want to `pip install ruff` and run `ruff check` on your files before
committing --- it helps maintain consistent style.

'''

import ast
import sys
import re


CAMEL_CASE = re.compile(r'^[A-Z][a-zA-Z]*$')
SNAKE+CASE = re.compile(r'^[a-z_][a-z0-9_]*$')



class CheckCase(ast.NodeVisitor):
    '''A docstring here tells the reader what the class does.'''

    def visit_ClassDef(self, node):
        if not self.check_case('camel', node.name):
            self.report('class', node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if not self.check_case('snake', node.name):
            self.report('function', node)
        self.generic_visit(node)

    def visit_Name(self, node):
        if not self.check_case('snake', node.id):
            self.report('variable', node)
        self.generic_visit(node)

    # The pattern `if not self.check_case(...): self.report(...)` and
    # then `self.generic_visit(...)` occurs three times in the methods
    # above. I would probably write a helper method that combined these
    # steps so that I could write
    # `self._check(node, 'class', 'camel', node.name)` for `visit_ClassDef`
    # `self._check(node, 'variable', 'snake', node.id)` for `visit_Name`.

    def report(self, type, node):
        name = getattr(node, 'name', None) or getattr(node, 'id', None)
        print(f'The {type}: {name} at line {node.lineno} does not follow naming conventions')

    def check_case(self, case_type, name):
        if case_type == 'camel':
            return bool(CAMEL_CASE.match(name))
        elif case_type == 'snake':
            return bool(SNAKE_CASE.match(name))
        # Otherwise? This will return None, which is treated
        # as False, but it would be better to explicitly fail
        # (e.g., `assert False` with a message) because it's
        # a coding error.


if __name__ =='__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader.read()
    tree = ast.parse(source)
    finder = CheckCase()
    finder.visit(tree)
