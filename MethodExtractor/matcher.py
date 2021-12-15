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
        FUNC_DEF = re.compile("^def")
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
    repo_regex = re.compile(r"/[a-zA-Z.]+(?!/)$")
    repo_name = re.search(repo_regex, repo_url)[0][1:-4]
    repo_dir = os.path.normpath("repos/" + repo_name)
    if os.path.exists(repo_dir):
        rmtree(repo_dir, onerror=rmtree_access_error_handler)
    Repo.clone_from(repo_url, repo_dir)
    source_files = []
    for root, dirs, files in os.walk(repo_dir):
        for dir_name in dirs:
            if dir_name == "src":
                for file in files:
                    if EXTENSION in file and "test" not in file:
                        source_files.append(os.path.normpath(root + "/" + file))
    return source_files


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


def find_python_arguments(source_file):
    with open(source_file, "r") as f:
        a = ast.parse(f.read(), mode="exec")
        functions = []
        for item in a.body:
            if type(item) is ast.FunctionDef:
                params = item.args.args
                defaults = item.args.defaults

                params.reverse()
                defaults.reverse()

                optionals = []
                # Find all the optional arguments
                for args in zip(params, defaults):
                    optionals.append((args[0].arg, args[1].value))

                # Find the required arguments
                required = []
                found = False
                for arg in params:
                    for optional in optionals:
                        if arg.arg in optional:
                            found = True
                            break
                    if not found:
                        required.append(arg.arg)
                    found = False

                functions.append((item.name, (len(required), len(optionals))))
        return functions


def find_params(language, source_file):
    functions = []
    if language == "python":
        functions = find_python_arguments(source_file)
    return functions


def calculate_ratios(language, repo_url, doc_url):
    doc_examples = get_documentation_examples(doc_url)
    # code_defs = get_public_methods(language, repo_url)
    # param_regex = re.compile(r"^(?:def|public).+\((?:.|\n)*?\)", re.MULTILINE)

    extension_finder(language)
    source_files = get_source_files(repo_url)
    functions = {}
    for source_file in source_files:
        funcs = find_params(language, source_file)
        for func in funcs:
            functions[func[0]] = {"source_file": source_file, "req_args": func[1][0], "opt_args": func[1][1]}

    files = {}
    for func in functions:
        if functions[func]["source_file"] in files:
            files[functions[func]["source_file"]] += 1
        else:
            files[functions[func]["source_file"]] = 1

    call_regex = re.compile(r"[\w]+(?=\().+?\)")
    args_regex = re.compile(r"(?<=\()(?:.|\n)+?(?=\))")
    method_calls = set()
    for ex in doc_examples:
        calls = re.findall(call_regex, ex)
        for call in calls:
            try:
                func_def = functions[call.split("(")[0]]
                args = re.search(args_regex, call)
                try:
                    num_args = len(args[0].split(","))
                except TypeError:
                    num_args = 0
                if num_args >= func_def["req_args"] and num_args <= (func_def["req_args"] + func_def["opt_args"]):
                    method_calls.add((func_def["source_file"], call.split("(")[0]))
                if len(method_calls) == len(functions):
                    break
            # Just because the found method call is not found in the public
            # API methods, does not mean it is incorrect, it could be calling
            # a method from a different library
            except KeyError:
                pass

    found_examples = {}
    for call in method_calls:
        if call[0] in found_examples:
            found_examples[call[0]] += 1
        else:
            found_examples[call[0]] = 1

    # print(files)
    # print(found_examples)

    example_count = 0
    classes_count = 0
    for examples in found_examples:
        example_count += found_examples[examples]
        if found_examples[examples] == files[examples]:
            classes_count += 1

    total_examples = 0
    total_classes = len(files)
    for file in files:
        total_examples += files[file]

    print(example_count/total_examples)
    print(classes_count/total_classes)
