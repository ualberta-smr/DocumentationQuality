import javalang


def find_java_arguments(source_file):
    functions = []
    with open(source_file, "r", encoding="utf-8") as f:
        try:
            tree = javalang.parse.parse(f.read())
            for file_item in tree.types:
                if type(file_item) is javalang.tree.ClassDeclaration:
                    for method in file_item.body:
                        if type(method) is javalang.tree.MethodDeclaration:
                            # NOTE: It may not be enough to get the number of parameters, may need to get type as well
                            # so when we try to match documentation examples we can check type of argument in doc example with type of parameter
                            # method.parameters[0].type.name
                            functions.append((file_item.name + "." + method.name, len(method.parameters)))
        except Exception as e:
            pass
            # print(e.description + " line " + str(e.at.position.line) + ", position" + str(e.at.position.column) + " " + source_file)
    return functions
