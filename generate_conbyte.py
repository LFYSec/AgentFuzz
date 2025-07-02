import ast
import os
import subprocess
import re
import platform
import json

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


def parser_result(text):
    # Get all matching items with non-greedy matching
    pattern = r"<<<<<<<<<<<<<<<< MATCH RESULT BEGIN >>>>>>>>>>>>>>>>\n(.*?)\n<<<<<<<<<<<<<<<< MATCH RESULT END >>>>>>>>>>>>>>>>"
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        print("No matches found.")
        return None

    last_match_str = matches[-1]

    try:
        # Safely convert a string dictionary to a Python dictionary
        data_dict = ast.literal_eval(last_match_str)
        return data_dict
    except Exception as e:
        print("Parsing failed:", e)
        return None

def is_windows():
    return platform.system() == "Windows"


def get_conbyte_result(input_vars, function_code):
    with open("./py-conbyte/test/my_tmp.py", "w") as f:
        f.write(function_code)
    results = []
    for key in input_vars:
        results.append(input_vars[key])
    with open("./py-conbyte/inputs.py","w") as f:
        f.write("INI_ARGS = " + json.dumps(results))
    PYTHON_EXECUTABLE = "python" if os.name == "nt" else "python3"
    # The target directory contains Pipfile and target scripts
    pipenv_project_dir = "./py-conbyte"

    command = ["pipenv", "run", PYTHON_EXECUTABLE, 
               "py-conbyte.py",
               "-i", "inputs.py",
               "test/my_tmp.py"]

    result = subprocess.run(command, cwd=pipenv_project_dir, 
                            capture_output=True, text=True)

    stdout = result.stdout
    stderr = result.stderr

    # print("Standard Error:")
    # print(stderr)
    # print(stdout)
    # print(parser_result(stdout))
    return parser_result(stdout)
