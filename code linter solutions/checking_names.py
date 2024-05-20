import ast
import string
import sys
class CheckCase(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        if not self.check_case('camel',node.name):
            self.report('class', node)
        self.generic_visit(node)
       

    def visit_FunctionDef(self, node):
        # print(node.args.args[0].arg)
        if not self.check_case('snake', node.name):
            self.report('function', node)
        self.generic_visit(node)

    def visit_Name(self, node):
        if not self.check_case('snake', node.id):
            self.report('variable', node)
        self.generic_visit(node)

    def report(self, type, node):
        name = getattr(node, 'name', None) or getattr(node,'id', None)
        print(f'The {type}: {name} at line {node.lineno} does not follow naming conventions')

    def check_case(self, case_type, name):
        if case_type == 'camel':
            return bool(re.match(r'^[A-Z][a-zA-Z]*$', name))
        elif case_type == 'snake':
            return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))
if __name__ =='__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader .read()
    tree = ast.parse(source)
    finder = CheckCase()
    finder.visit(tree)