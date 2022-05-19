import esprima
import traceback
import re
import os
import csv


def preprocess(source_file):
    preprocessed_filename = source_file.split(".")[0] + "_temp." + \
                            source_file.split(".")[1]
    with open(source_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        with open(preprocessed_filename, "w", encoding="utf-8") as out:
            function_or_class = re.compile("\bfunction\b|\bclass\b")
            # We need a write flag because we want to ignore
            # `export default { ... };` blocks
            write = True
            for line in lines:
                # esprima can not parse import statements
                if not line.startswith("import"):
                    # esprima can not parse export lines
                    if line.startswith("export "):
                        if line.startswith("export default "):
                            if re.search(function_or_class, line):
                                line = line.replace("export default ", "")
                            else:
                                write = False
                        else:
                            line = line.replace("export ", "")
                    if line == "};":
                        write = True
                    if write:
                        out.write(line)
    return preprocessed_filename


def find_javascript_arguments(source_file):
    functions = []
    preprocessed_filename = preprocess(source_file)
    with open(preprocessed_filename, "r", encoding="utf-8") as f:
        try:
            tree = esprima.parse(f.read())
            private_function = re.compile("^_(?!_)")
            for item in tree.body:
                if type(item) is esprima.nodes.ExpressionStatement or \
                        type(item) is esprima.nodes.AsyncFunctionExpression:
                    left = item.expression.left
                    right = item.expression.right
                    if type(right) is esprima.nodes.FunctionExpression:
                        if left.property.name != "exports" and \
                                not re.match(private_function, left.property.name):
                            if type(left.object) is esprima.nodes.Identifier:
                                functions.append((
                                                 left.object.name + "." + left.property.name,
                                                 len(right.params)))
                            else:
                                functions.append((
                                                 left.object.object.name + left.object.property.name,
                                                 len(right.params)))
                elif type(item) is esprima.nodes.FunctionDeclaration or \
                        type(item) is esprima.nodes.AsyncFunctionDeclaration:
                    if not re.match(private_function, item.id.name):
                        functions.append((item.id.name, len(item.params)))
                elif type(item) is esprima.nodes.ArrowFunctionExpression or \
                        type(item) is esprima.nodes.AsyncArrowFunctionExpression:
                    print(preprocessed_filename)
                    print("New function type")
        except:
            print(preprocessed_filename)
            print(traceback.format_exc())
    os.remove(preprocessed_filename)
    return functions


def javascript_match(repo_name, examples, functions, classes):
    method_calls = set()
    with open("results/" + repo_name + ".csv", "w", encoding="utf-8",
              newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["Example", "Extracted Function", "Linked Function", "Source File",
             "Matched"])
        call_regex = re.compile(r"(?:\w+\.)?\w+(?=\()")
        for ex in examples:
            example = ex[0]
            found_calls = re.findall(call_regex, example)
            calls = []
            [calls.append(item) for item in found_calls if item not in calls]
            for call in calls:
                func_def = None
                multiple_potential_methods = False
                potential_method = call
                if call not in functions:
                    function_split = call.split(".")
                    if len(function_split) > 1:
                        potential_methods = set()
                        for key in functions:
                            if function_split[-1] == key.split(".")[-1]:
                                potential_methods.add(key)
                        if len(potential_methods) > 1:
                            multiple_potential_methods = True
                        elif len(potential_methods) == 1:
                            potential_method = next(iter(potential_methods))
                            func_def = functions[potential_method]
                else:
                    func_def = functions[potential_method]
                if func_def:
                    function_calls = re.findall(re.compile(
                        r"%s\([a-zA-Z_:.,/\\ =(){}\'\"|]*?\)"
                        % call.replace(".", "\.")), example)
                    for function_call in function_calls:
                        num_args = len(function_call.split(", "))
                        if num_args in func_def["req_args"]:
                            method_calls.add(
                                (func_def["source_file"], potential_method))
                            writer.writerow([example, call, potential_method,
                                             func_def["source_file"], "True"])
                        else:
                            writer.writerow([example, call, potential_method,
                                             func_def["source_file"], "False"])
                else:
                    if multiple_potential_methods:
                        linked_methods = []
                        src_files = []
                        for method in potential_methods:
                            linked_methods.append(method)
                            src_files.append(functions[method]["source_file"])
                        writer.writerow([example, call,
                                         "\n".join(linked_methods),
                                         "\n".join(src_files), "False"])
                    else:
                        writer.writerow([example, call, "N/A", "N/A", "N/A"])
    return method_calls
