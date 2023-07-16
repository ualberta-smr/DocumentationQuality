import ast
import logging
import re
import csv
import os
import inspect
import importlib
import subprocess
import sys
from typing import Dict


def find_python_arguments(source_file):
    with open(source_file, "r", encoding="utf-8") as f:
        functions = []
        try:
            a = ast.parse(f.read(), mode="exec")
            private_function = re.compile("^_(?!_)")
            for file_item in a.body:
                if type(file_item) is ast.ClassDef:
                    for class_item in file_item.body:
                        if type(class_item) is ast.FunctionDef:
                            # We ignore methods that start with "_" because they are
                            # typically considered private methods
                            if not re.match(private_function, class_item.name):
                                func_name, required, optionals = _extract_python_ast_args(class_item, True)
                                functions.append(((file_item.name + "." + func_name), required, optionals))
                if type(file_item) is ast.FunctionDef:
                    if not re.match(private_function, file_item.name):
                        func_name, required, optionals = _extract_python_ast_args(file_item, False)
                        functions.append(
                            ((os.path.split(os.path.split(source_file)[0])[1] + "." + func_name), required, optionals))
        except Exception as e:
            pass
    return functions


def _extract_python_ast_args(func_def, class_method):
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
    for arg in params:
        found = False
        for optional in optionals:
            if arg.arg == optional:
                found = True
                break
        if not found:
            required.append(arg.arg)
    if func_def.args.kwarg:
        optionals.append(func_def.args.kwarg.arg)
    # Remove the self parameter from class methods
    if class_method:
        try:
            required.remove("self")
        except ValueError:
            pass
    return func_def.name, required, optionals


def _find_args(example):
    parse = (None, [])
    a = None
    try:
        a = ast.parse(example)
    except SyntaxError:
        try:
            a = ast.parse("".join(example.split(" ")[1:]))
        except SyntaxError:
            pass
            # print(example)
            # print(traceback.format_exc())
    if a:
        list_args = []
        try:
            if type(a.body[0].value) is ast.Constant:
                list_args.append(a.body[0].value)
            elif hasattr(a.body[0].value, "keywords"):
                for arg in a.body[0].value.args:
                    if hasattr(arg, "value"):
                        list_args.append(arg.value.id)
                    else:
                        list_args.append(arg.id)
                for arg in a.body[0].value.keywords:
                    if arg.arg:
                        list_args.append(arg.arg)
                    else:
                        list_args.append(arg.value.id)
            else:
                for arg in a.body[0].value.args:
                    list_args.append(arg.id)
            if list_args:
                if hasattr(a.body[0].value.func, "value"):
                    temp = []
                    for part in ast.walk(a.body[0].value.func):
                        if hasattr(part, "id"):
                            temp.append(part.id)
                        elif hasattr(part, "attr"):
                            temp.append(part.attr)
                    temp.reverse()
                    parse = (".".join(temp), list_args)
                else:
                    parse = (a.body[0].value.func.id, list_args)
        except:
            pass
            # print(example)
            # print(traceback.format_exc())
    return parse


def _find_func_def(call, functions, classes):
    func_def = None
    matched_methods = []
    potential_classes = []
    name = call[0]
    if call[0]:
        if call[0] in functions:
            func_def = functions[name]
        elif call[0].split(".")[-1] in functions:
            name = call[0].split(".")[-1]
            func_def = functions[name]
        elif call[0].split(".")[-1] in classes:
            name = call[0].split(".")[-1] + ".__init__"
            if name in functions:
                func_def = functions[name]
            else:
                potential_classes.append(name)
        else:
            potential_methods = []
            for key, value in functions.items():
                potential = key.split(".")[-1]
                if call[0].split(".")[-1] == potential:
                    potential_methods.append((key, value))
            if potential_methods:
                for po in potential_methods:
                    potential = po[1]
                    arg_count = 0
                    for arg in call[1]:
                        if arg in potential["req_args"] or arg in potential["opt_args"]:
                            arg_count += 1
                    if arg_count == len(call[1]):
                        matched_methods.append(po)
            for key, _ in classes.items():
                if call[0].split(".")[-1].lower() == key.lower():
                    potential_classes.append(key)

    return name, func_def, matched_methods, potential_classes


def python_match_signatures(repo_name, examples, functions, classes):
    method_calls = set()
    links = []
    for ex in examples:
        example = ex[0]
        link = [example]
        call = _find_args(example)
        if call:
            name, func_def, matched_methods, potential_classes = _find_func_def(call, functions, classes)
            link.append(call)
            if func_def:
                method_calls.add((func_def["source_file"], call[0]))
                link.append((name, func_def["req_args"] + func_def["opt_args"]))
                link.append(func_def["source_file"] if func_def["source_file"] else "N/A")
                link.append(True)
            elif len(matched_methods) == 1:
                method_calls.add((matched_methods[0][1]["source_file"], matched_methods[0][0]))
                link.append(
                    (matched_methods[0][0], matched_methods[0][1]["req_args"] + matched_methods[0][1]["opt_args"]))
                link.append(matched_methods[0][1]["source_file"])
                link.append(True)
            elif len(matched_methods) > 1:
                methods = []
                for match in matched_methods:
                    methods.append((match[0], match[1]["req_args"] + match[1]["opt_args"]))
                link.append(methods)
                link.append("N/A")
                link.append(False)
            elif len(potential_classes) > 0:
                link.append(potential_classes)
                link.append("N/A")
                link.append(False)
            else:
                link.append("N/A")
                link.append("N/A")
                link.append(False)
        else:
            link.append("N/A")
            link.append("N/A")
            link.append("N/A")
            link.append("N/A")
        links.append(link)
    seen = set()
    with open("MethodLinker/results/signatures/" + repo_name + ".csv", "w", encoding="utf-8",
              newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["Example", "Extracted Function", "Linked Function", "Source File", "Matched"])
        for link in links:
            if (link[0], link[3]) not in seen:
                writer.writerow(link)
                seen.add((link[0], link[3]))
    return method_calls


def python_match_examples(repo_name, examples, functions, classes):
    method_calls = set()
    links = []
    var_declarations = dict()

    install(repo_name)
    module = importlib.import_module(repo_name)

    call_regex = re.compile(r"(?:\w+\.)+\w+(?=\()")
    for ex in examples:
        example = ex[0]
        found_calls = re.findall(call_regex, example)
        var_declarations.update(get_declared_variable_mapping(example, classes))
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
                        func_def = match_call_with_other_class_functions(
                            module, classes, functions, call, var_declarations)

            else:
                func_def = functions[call]
            if func_def:
                function_calls = re.findall(re.compile(
                    r"\b%s\([a-zA-Z0-9_:.,/\\ =(){}\'\"|\[\]\n]*?\)"
                    % call.replace(".", "\.")), example)
                for function_call in function_calls:
                    try:
                        a = ast.parse(function_call)
                        if type(a.body[0].value) is ast.Constant:
                            num_args = 1
                        elif hasattr(a.body[0].value, "keywords"):
                            num_args = len(a.body[0].value.args) + len(
                                a.body[0].value.keywords)
                        else:
                            num_args = len(a.body[0].value.args)
                    except:
                        num_args = 0
                    if len(func_def["req_args"]) <= num_args <= (sys.maxsize if "kwargs" in func_def["opt_args"] else (
                            len(func_def["req_args"]) + len(func_def["opt_args"]))):
                        method_calls.add((func_def["source_file"], call))
                        links.append(
                            [example, call, call.split(".")[1] if len(
                                call.split(".")) > 1 else call,
                             func_def["source_file"],
                             "True"])
                    else:
                        links.append(
                            [example, call, call.split(".")[1] if len(
                                call.split(".")) > 1 else call,
                             func_def["source_file"],
                             "False"])
            else:
                potential_class = call.split(".")[-1]
                if potential_class in classes:
                    links.append([example, potential_class, "__init__",
                                  classes[potential_class][
                                      "source_file"], "True"])
                else:
                    links.append([example, call, "N/A", "N/A", "N/A"])
    seen = set()
    with open("MethodLinker/results/examples/" + repo_name + ".csv", "w", encoding="utf-8",
              newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["Example", "Extracted Function", "Linked Function", "Source File",
             "Matched"])
        for link in links:
            if (link[0], link[1]) not in seen:
                writer.writerow(link)
                seen.add((link[0], link[1]))

    return method_calls


def get_declared_variable_mapping(example_code: str, classes: Dict) -> Dict:
    var_declarations = dict()
    func_call_assign_regex = r"(\w+)\s*=\s*(?:\w+\.)+(\w+(?=\())"
    import_regex = r"(?:^\s*(?:import)\s+(\w+(?:\.\w+)*)\s+(?:as)\s+(\w+))|(?:^\s*(?:from)\s+(?:\w+(?:\.\w+)*)\s(?:import)\s+(\w+(?:\.\w+)*)(?:\s+(?:as)\s+(\w+))?)"
    lines = example_code.split('\n')
    for line in lines:
        try:
            line = preprocess_doc_example_line(line)
            if not line:
                continue
            parsed_line = "" if not ast.parse(line.strip()).body else ast.parse(line.strip()).body[0]
            if parsed_line and type(parsed_line) == ast.Import:
                import_values = re.findall(re.compile(import_regex), line)[0]
                import_values = [value for value in import_values if value]
                if len(import_values) == 2:
                    var_declarations[import_values[1]] = import_values[0]

            elif parsed_line and type(parsed_line) == ast.Assign:
                func_call_assign = re.findall(func_call_assign_regex, line)
                func_call_assign = func_call_assign[0] if func_call_assign else None

                if func_call_assign and len(func_call_assign) == 2 and func_call_assign[1] in classes.keys():
                    var_declarations[func_call_assign[0]] = func_call_assign[1]

        except Exception as e:
            logging.debug(f"Error in get_declared_variable_mapping. Example code line: \n{line}")
            logging.debug(e)

    return var_declarations


def preprocess_doc_example_line(line: str) -> str:
    jupyter_notebook_prefix = r"(?:^In\s?\[\d+\]\:\s*)|(?:^Out\s?\[\d+\]\:\s*)"
    prompt_regex = r"(?:^>>>\s*)"
    rest_line = r"(.*\S)$"
    code_line = f'(?:{jupyter_notebook_prefix}|{prompt_regex})?{rest_line}'

    processed_line = re.findall(re.compile(code_line), line)
    processed_line = processed_line[0] if len(processed_line) > 0 else ''

    return processed_line


def match_call_with_other_class_functions(module, classes: Dict, functions: Dict, call: str,
                                          var_declarations: Dict) -> Dict:
    # match df -> DataFrame
    # Traverse through code and find class declarations as variables
    # e.g: df1 = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list("ABCD"))
    # we need to know that Dataframe is a class and put df in a dict matched with DataFrame
    function_split = call.split(".")
    class_name = function_split[0]
    function_name = function_split[-1]

    actual_class_name = var_declarations[class_name] if class_name in var_declarations else \
        class_name if class_name in classes.keys() else None

    if actual_class_name:
        similar_funcs = [s for s in functions.keys() if function_split[1] in s.split('.')]
        if len(similar_funcs) > 0:
            for func in similar_funcs:
                try:
                    class_members = inspect.getmembers(getattr(module, actual_class_name))
                    actual_func = [member for member in class_members if not 'NA' in member and function_name in member]
                    if actual_func:
                        actual_func_qualified_name = actual_func[0][1].__qualname__
                        actual_func_module = actual_func[0][1].__module__

                        # e.g: 1. 'NDFrame' in ['NDFrame', 'head'] ;
                        # e.g: 2.  'indexes' in 'date_range'
                        if func.split('.')[0] in actual_func_qualified_name.split('.'):
                            return functions[func]

                        # e.g: 1. 'NDFrame' in ['pandas', 'core', 'generic'] ;
                        # e.g: 2. 'indexes' in ['pandas', 'core', 'indexes', 'datetimes']
                        if func.split('.')[0] in actual_func_module.split('.'):
                            return functions[func]

                except Exception as e:
                    logging.debug(e)
                    logging.debug(function_split[0] + " " + function_split[1])
                    logging.debug(call)

    return None


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
