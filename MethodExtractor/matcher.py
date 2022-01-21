import html
import re
import os
import ast

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from git import Repo
from shutil import rmtree


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

EXTENSION = None
FUNC_DEF = None
DEFAULT_VALUES = False


def extension_finder(language):
    language = language.lower().strip()
    global EXTENSION
    global FUNC_DEF
    global DEFAULT_VALUES
    if language == "python":
        EXTENSION = ".py"
        # Accounts for both 2 and 4 space indents
        FUNC_DEF = re.compile("(?:^|^ {2,4})def (?!_)")
        DEFAULT_VALUES = True
    elif language == "java":
        EXTENSION = ".java"


def get_documentation_examples(url):
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    raw_examples = soup.find_all("code") + soup.find_all("pre")
    doc_examples = []

    for raw_example in raw_examples:
        example = raw_example.get_text()
        if "(" in example:
            doc_examples.append(example)
    return doc_examples


# Taken from: https://stackoverflow.com/questions/2656322/shutil-rmtree-fails-on-windows-with-access-is-denied
# User: Justin Peel
# At 15:22pm MST
def rmtree_access_error_handler(func, path, exc_info):
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def get_source_files(repo_url):
    repo_regex = re.compile(r"(?<=/)[a-zA-Z.]+(?!/)$")
    repo_name = re.search(repo_regex, repo_url)[0][:-4]
    repo_dir = os.path.normpath("repos/" + repo_name)
    if os.path.exists(repo_dir):
        rmtree(repo_dir, onerror=rmtree_access_error_handler)
    Repo.clone_from(repo_url, repo_dir)
    source_files = []
    src_dir = None
    # Only look at the top level directory in this loop
    for root, dirs, files in os.walk(repo_dir):
        for dir_name in dirs:
            if dir_name == "src" or dir_name == repo_name:
                src_dir = os.path.normpath(root + "/" + dir_name)
                break
        for file in files:
            if EXTENSION in file and "test" not in file:
                source_files.append(os.path.normpath(root + "/" + file))
        break
    # If we found a src directory, loop through all the files (subdirectory too)
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if EXTENSION in file and "test" not in file:
                source_files.append(os.path.normpath(root + "/" + file))
    return source_files


# NOT USED
def get_public_methods(language, repo_url):
    extension_finder(language)
    source_files = get_source_files(repo_url)
    code_defs = []
    code_def = []
    save_snippet = False
    for src in source_files:
        with open(src, encoding="utf-8") as file:
            for line in file:
                if re.search(FUNC_DEF, line):
                    save_snippet = True
                if save_snippet:
                    code_def.append(line)
                if ")" in line:
                    save_snippet = False
                    if code_def:
                        code_defs.append(code_def.copy())
                        code_def.clear()
    for index, code_def in enumerate(code_defs):
        code_defs[index] = "".join(code_def)

    return code_defs


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
    return func_def.name, ((len(required) - 1 if class_method else len(required)), len(optionals))


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


def find_params(language, source_file):
    functions = []
    if language == "python":
        functions = find_python_arguments(source_file)
    return functions


def get_methods_and_classes(language, repo_url):
    source_files = get_source_files(repo_url)
    functions = {}
    for source_file in source_files:
        funcs = find_params(language, source_file)
        for func in funcs:
            functions[func[0]] = {"source_file": source_file,
                                  "req_args": func[1][0],
                                  "opt_args": func[1][1]}
    classes = {}
    for func in functions:
        f = func.split(".")
        if len(f) > 1:
            classes[f[0]] = {"source_file": functions[func]["source_file"]}

    return functions, classes


def calculate_ratios(language, repo_url, pages):
    extension_finder(language)
    functions, classes = get_methods_and_classes(language, repo_url)
    doc_examples = []
    for page in pages:
        try:
            doc_examples.extend(get_documentation_examples(page))
        except:
            pass

    call_regex = re.compile(r"(?:\w+\.)?\w+(?=\()")
    args_regex = re.compile(r"(?<=\()(?:.|\n)+?(?=\))")
    method_calls = set()
    for example in doc_examples:
        calls = re.findall(call_regex, example)
        for call in calls:
            func_def = None
            function = call.split("(")[0].lower()
            if function not in functions:
                function_split = function.split(".")
                if len(function_split) > 1:
                    if function_split[1] in functions:
                        func_def = functions[function_split[1]]
            else:
                func_def = functions[function]
            if func_def:
                args = re.search(args_regex, example)
                try:
                    num_args = len(args[0].split(","))
                except TypeError:
                    num_args = 0
                if func_def["req_args"] <= num_args <= (func_def["req_args"] + func_def["opt_args"]):
                    method_calls.add((func_def["source_file"], function))

    example_count = len(method_calls)
    classes_count = 0
    for examples in method_calls:
        example = examples[1].split(".")
        # If we cannot split anything then the method is not in a class
        if len(example) > 1:
            if example[0].lower() in classes:
                classes_count += 1

    total_classes = len(classes)
    total_methods = len(functions)
    return example_count, total_methods, classes_count, total_classes
