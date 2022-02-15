import ast


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
                        if not class_item.name.startswith("_"):
                            func_name, args = extract_python_ast_args(class_item, True)
                            functions.append(((file_item.name + "." + func_name).lower(), args))
            if type(file_item) is ast.FunctionDef:
                if not file_item.name.startswith("_"):
                    functions.append(extract_python_ast_args(file_item, False))
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
    # TODO: Account for kwargs here
    for arg in params:
        for optional in optionals:
            if arg.arg == optional:
                found = True
                break
        if not found:
            required.append(arg.arg)
        found = False
    # The ternary -1 accounts for the "self" parameter on class methods
    return func_def.name, ((len(required) - 1 if class_method else len(required)), len(optionals))