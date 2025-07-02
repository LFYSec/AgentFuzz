import ast
import os
import subprocess
import re
import platform

def convert_bracket_to_at(expression):
    # Regular expressions match the form `text[...]`
    pattern = r"text\[(\d+|-?\d+)\]"
    

    converted_expression = re.sub(pattern, r'text.at(\1)', expression)
    
    return converted_expression

# Function to convert Python constraints to Z3 constraints
def convert_to_z3(constraint):
    # Convert logical operators
    # Because the constraints in _norm_text will cause the & symbol to report an error, comment out this line
    # constraint = constraint.replace(' and ', ' & ')
    constraint = constraint.replace(' or ', ' | ')
    constraint = constraint.replace('not ', '~')

    # Convert membership tests (e.g., 'element' in container)
    while ' in ' in constraint:
        parts = constraint.split(' in ', 1)
        if len(parts) == 2:
            element = parts[0].strip().strip("'").strip('"')
            container = parts[1].strip()
            constraint = f"Contains({container}, '{element}')"

    # Handle length check (e.g., len(langchain_object.input_keys) == 0)
    if 'len(' in constraint:
        start = constraint.index('len(') + 4
        end = constraint.index(')', start)
        inner = constraint[start:end].strip()
        constraint = constraint.replace(f'len({inner})', f'Length({inner})')
    
    constraint = convert_bracket_to_at(constraint)

    return constraint

# Class to infer variable types from the AST
class TypeInference(ast.NodeVisitor):
    def __init__(self):
        self.variable_types = {}
        self.supported = True

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.variable_types.setdefault(node.id, 'Unknown')

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Name):
            self.variable_types[node.value.id] = 'Bool'
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        for value in node.values:
            if isinstance(value, ast.Name):
                self.variable_types[value.id] = 'Bool'
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id == 'strip':
                if isinstance(node.args[0], ast.Name):
                    self.variable_types[node.args[0].id] = 'String'
            elif node.func.id == 'isinstance':
                self.supported = False
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.Not):
            if isinstance(node.operand, ast.Name):
                self.variable_types[node.operand.id] = 'Bool'
        self.generic_visit(node)

# Function to infer variable types from a constraint
def infer_variable_types(constraint):
    tree = ast.parse(constraint)
    inference = TypeInference()
    inference.visit(tree)
    if not inference.supported:
        print(f"Error: The constraint '{constraint}' contains unsupported expressions.")
        return None
    return inference.variable_types

def parser_result(result):
    pattern = re.compile(r'\[(.*?)\]')


    match = pattern.search(result)
    if match:
        inner_str = match.group(1)
        if "," in inner_str:
            pairs = inner_str.split(', ')
        else:
            pairs = [inner_str]

        result_dict = {}
        for pair in pairs:
            key, value = pair.split(' = ')
            print(value)
            result_dict[key.strip()] = " " + str(value.strip()[1:-1]) + " "

        return result_dict
    return {}

def is_windows():
    return platform.system() == "Windows"

# Read constraints from the file
def get_z3_result(constraint, tmp_file_path = "/tmp/z3_script_tmp.py"):

        if tmp_file_path == "/tmp/z3_script_tmp.py" and is_windows():
            tmp_file_path = "./tmp/z3_script_tmp.py"

        variable_types = infer_variable_types(constraint)

        if variable_types is None:
            return {}

        # Convert to Z3 constraint
        z3_constraint = convert_to_z3(constraint)

        # Define Z3 variables
        z3_vars = "\n".join(
            [f"{var} = Bool('{var}')" if type_ == 'Bool' else f"{var} = String('{var}')" for var, type_ in variable_types.items()]
        )

        # Adjust the order of operations to ensure correct evaluation
        if '&' in z3_constraint:
            parts = z3_constraint.split(' & ')
            for idx, part in enumerate(parts):
                if 'Contains' in part:
                    parts[idx] = f'({part})'
            z3_constraint = ' & '.join(parts)

        # Generate Z3 script
        z3_script = f"""
from z3 import *

# Create Z3 variables
{z3_vars}

# Create Z3 solver
solver = Solver()

# Add constraints
solver.add({z3_constraint})

# Check satisfiability
if solver.check() == sat:
    model = solver.model()
    print(model)
else:
    print("Problem {constraint}: No solution satisfies the constraints")
"""

        # Save the generated Z3 script to a file
        with open(tmp_file_path, 'w') as script_file:
            script_file.write(z3_script)
        PYTHON_EXECUTABLE = "python" if os.name == "nt" else "python3"
        result = subprocess.run([PYTHON_EXECUTABLE,'-u', tmp_file_path], capture_output=True, text=True)
        # Get stdout, stderr
        stdout = result.stdout
        stderr = result.stderr

        # Printing Output
        print("Standard Output:")
        print(stdout)
        if "No solution satisfies the constraints" in stdout:
            return {}
        else:
            return parser_result(stdout)

if __name__ == '__main__':
    print(get_z3_result("'source_documents' in s",tmp_file_path = "tmp.py"))