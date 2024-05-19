import ast
import string
import sys
class CheckCase(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        if not self.check_case('camel',node):
            self.report('class', node)
        self.generic_visit(node)
       

    def visit_FunctionDef(self, node):
        if not self.check_case('snake', node):
            self.report('function', node)
        self.generic_visit(node)

    def visit_Name(self, node):
        if not self.check_case('snake', node):
            self.report('variable', node)
        self.generic_visit(node)

    def report(self, type, node):
        print(f'The {type}: {node.name} at line {node.lineno} does not follow naming conventions')

    def check_case(self, name, node):
        letters = set(string.ascii_uppercase) & set(node.name)
        print(letters)
        print(node.name)
        if name == 'camel':
            return True if letters and not '_' in node.name else False
        elif name == 'snake':
            return True if '_' in node.name and len(letters) == 0 else False
        else:
            raise ValueError('Unknown case')    
        
if __name__ =='__main__':
    with open(sys.argv[1], 'r') as reader:
        source = reader .read()
    tree = ast.parse(source)
    finder = CheckCase()
    finder.visit(tree)