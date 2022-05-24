import javalang
import csv
import re


def find_java_arguments(source_file):
    functions = []
    with open(source_file, "r", encoding="utf-8") as f:
        try:
            tree = javalang.parse.parse(f.read())
            for file_item in tree.types:
                if type(file_item) is javalang.tree.ClassDeclaration:
                    for method in file_item.body:
                        if type(method) is javalang.tree.ConstructorDeclaration:
                            functions.append(
                                (file_item.name, len(method.parameters)))
                        if type(method) is javalang.tree.MethodDeclaration:
                            if len(method.modifiers) > 0:
                                for modifier in method.modifiers:
                                    if modifier == "public":
                                        # NOTE: It may not be enough to get the
                                        # number of parameters, may need to get
                                        # type as well. So when we try to match
                                        # documentation examples we can check
                                        # type of argument in doc example with
                                        # type of parameter:
                                        # method.parameters[0].type.name
                                        functions.append(
                                            (file_item.name + "."
                                             + method.name,
                                             len(method.parameters)))
                                        break
        except Exception as e:
            pass
            # print(e.description + " line " +
            #       str(e.at.position.line) + ", position" +
            #       str(e.at.position.column) + " " + source_file)
    return functions


def java_match(repo_name, examples, functions, classes):
    method_calls = set()
    links = []
    call_regex = re.compile(r"(?:\w+\.)?\w+(?=\()")
    for ex in examples:
        example = ex[0]
        found_calls = re.findall(call_regex, example)
        calls = []
        [calls.append(item) for item in found_calls if item not in calls]
        for call in calls:
            func_def = None
            multiple_potential_methods = False
            potential_methods = set()
            potential_method = call
            if call not in functions:
                function_split = call.split(".")
                if len(function_split) > 1:
                    method_call = function_split[-1]
                    potential_classes = set()
                    for key, _ in functions.items():
                        key_split = key.split(".")
                        if len(key_split) > 1 and \
                                method_call == key_split[1]:
                            potential_classes.add(key_split[0])
                    for cls in potential_classes:
                        if cls in example:
                            potential_methods.add(cls + "." + method_call)
                    if len(potential_methods) > 1:
                        multiple_potential_methods = True
                        # This is the path where func_def is (still) None
                    elif len(potential_methods) == 1:
                        potential_method = next(iter(potential_methods))
                        func_def = functions[potential_method]
            else:
                func_def = functions[potential_method]
            if func_def:
                # TODO: Will not catch foo(bar(0), bar(1)), will only get
                # foo(bar(0)
                function_calls = re.findall(re.compile(
                    r"%s\([a-zA-Z0-9_:.,/\\ =(){}\'\"|\[\]]*?\)"
                    % call.replace(".", "\.")), example)
                for function_call in function_calls:
                    num_args = len(function_call.split(", "))
                    if num_args in func_def["req_args"]:
                        method_calls.add(
                            (func_def["source_file"], potential_method))
                        links.append([example, call, potential_method,
                                         func_def["source_file"], "True"])
                    else:
                        links.append([example, call, potential_method,
                                         func_def["source_file"], "False"])
            else:
                if multiple_potential_methods:
                    linked_methods = []
                    src_files = []
                    for method in potential_methods:
                        linked_methods.append(method)
                        src_files.append(functions[method]["source_file"])
                    links.append(
                        [example, call, "\n".join(linked_methods),
                         "\n".join(src_files), "False"])
                else:
                    potential_class = call.split(".")[-1]
                    if potential_class in classes:
                        links.append(
                            [example, potential_class, potential_class,
                             classes[potential_class]["source_file"],
                             "True"])
                    else:
                        links.append(
                            [example, call, "N/A", "N/A", "N/A"])
    seen = set()
    with open("results/" + repo_name + ".csv", "w", encoding="utf-8",
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
