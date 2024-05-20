import ast
import sys
class CheckDocStrings(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node):
            self.report('function', node)    
        self.generic_visit(node)

    def visit_ClassDef(self,node):
        if not ast.get_docstring(node):
            self.report('class', node)
        self.generic_visit(node)
    
    def report(self, node_type, node):
        print(f'the {node_type} {node.name} does not have a doc string')

with open(sys.argv[1], 'r') as reader:
    source = reader .read()
tree = ast.parse(source)
finder = CheckDocStrings()
finder.visit(tree)