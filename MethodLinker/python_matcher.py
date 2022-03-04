import ast
import sys
import re
import csv


def find_python_arguments(source_file):
    with open(source_file, "r", encoding="utf-8") as f:
        a = ast.parse(f.read(), mode="exec")
        functions = []
        for file_item in a.body:
            if type(file_item) is ast.ClassDef:
                for class_item in file_item.body:
                    if type(class_item) is ast.FunctionDef:
                        # We ignore methods that start with "_" because they are
                        # typically considered private methods
                        func_name, args = extract_python_ast_args(class_item, True)
                        functions.append(((file_item.name + "." + func_name), args))
            if type(file_item) is ast.FunctionDef:
                func_name, args = extract_python_ast_args(file_item, False)
                functions.append(((source_file.split("\\")[0] + "." + func_name), args))
    return functions


def extract_python_ast_args(func_def, class_method):
    params = func_def.args.args
    defaults = func_def.args.defaults

    params.reverse()
    defaults.reverse()

    optionals = []
    # Find all the optional arguments
    for args in zip(params, defaults):
        optionals.append(args[0].arg)
    # Find the required arguments
    required = []
    found = False
    for arg in params:
        for optional in optionals:
            if arg.arg == optional:
                found = True
                break
        if not found:
            required.append(arg.arg)
        found = False
    # The ternary -1 accounts for the "self" parameter on class methods
    return func_def.name, ((len(required) - 1 if class_method else len(required)), (sys.maxsize if hasattr(func_def.args, "kwarg") else len(optionals)))


def python_match(repo_name, examples, functions, classes):
    method_calls = set()
    with open("results/" + repo_name + ".csv", "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Example", "Extracted Function", "Linked Function", "Source File", "Linked"])
        call_regex = re.compile(r"(?:\w+\.)?\w+(?=\()")
        for ex in examples:
            example = ex[0]
            found_calls = re.findall(call_regex, example)
            calls = []
            # Remove duplicate found calls
            [calls.append(item) for item in found_calls if item not in calls]
            for call in calls:
                func_def = None
                # Check if the function exists in our dictionary
                if call not in functions:
                    function_split = call.split(".")
                    # If not then maybe it does if we remove the first prefix
                    # e.g., nltk.nltk.get -> nltk.get
                    if len(function_split) > 1:
                        if function_split[1] in functions:
                            func_def = functions[function_split[1]]
                else:
                    func_def = functions[call]
                if func_def:
                    function_calls = re.findall(re.compile(r"%s\([a-zA-Z_:.,/\\ =(){}\'\"]*?\)" % call.replace(".", "\.")), example)
                    for function_call in function_calls:
                        try:
                            a = ast.parse(function_call)
                            if type(a.body[0].value) is ast.Constant:
                                num_args = 1
                            elif hasattr(a.body[0].value, "keywords"):
                                num_args = len(a.body[0].value.args) + len(a.body[0].value.keywords)
                            else:
                                num_args = len(a.body[0].value.args)
                        except:
                            num_args = 0
                        if func_def["req_args"] <= num_args <= (func_def["req_args"] + func_def["opt_args"]):
                            method_calls.add((func_def["source_file"], call))
                            writer.writerow([example, call, call, func_def["source_file"], "True"])
                        else:
                            writer.writerow([example, call, call, func_def["source_file"], "False"])
                else:
                    potential_class = call.split(".")[-1]
                    if potential_class in classes:
                        writer.writerow([example, potential_class, "__init__", classes[potential_class]["source_file"], "True"])
                    else:
                        writer.writerow([example, call, "N/A", "N/A", "N/A"])
    return method_calls
