import html
import urllib.error
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from pathlib import PurePath

from .java_matcher import *
from .python_matcher import *
from .javascript_matcher import *
from ..util import HEADERS

EXTENSION = None
LANGUAGE = None


def calculate_ratios(language, repo_name, repo_path, doc_url, pages, check_examples):
    make_directories_for_method_linker()
    set_extension(language)
    functions, classes = get_methods_and_classes(repo_name, repo_path)
    if functions and classes:
        doc_examples = get_doc_examples(check_examples, doc_url, pages)
        method_calls = set()

        if LANGUAGE == "python":
            if check_examples:
                method_calls = python_match_examples(repo_name, doc_examples, functions, classes)
            else:
                method_calls = python_match_signatures(repo_name, doc_examples, functions, classes)

        elif LANGUAGE == "java":
            if check_examples:
                method_calls = java_match_examples(repo_name, doc_examples, functions, classes)
            else:
                method_calls = java_match_signatures(repo_name, doc_examples, functions, classes)

        elif LANGUAGE == "javascript":
            if check_examples:
                method_calls = javascript_match_examples(repo_name, doc_examples, functions, classes)
            else:
                method_calls = javascript_match_signatures(repo_name, doc_examples, functions, classes)

        example_count = len(method_calls)
        seen_classes = set()
        for method_call in method_calls:
            example = method_call[1].split(".")
            if example[0] in classes:
                seen_classes.add(example[0])

        return example_count, len(functions), len(seen_classes), len(classes)
    else:
        return None, None, None, None


def make_directories_for_method_linker():
    if not os.path.isdir("MethodLinker/results"):
        os.mkdir("MethodLinker/results")
    if not os.path.isdir(os.path.normpath("MethodLinker/results/examples")):
        os.mkdir(os.path.normpath("MethodLinker/results/examples"))
    if not os.path.isdir(os.path.normpath("MethodLinker/results/signatures")):
        os.mkdir(os.path.normpath("MethodLinker/results/signatures"))


def set_extension(language):
    language = language.lower().strip()
    global EXTENSION
    global LANGUAGE
    if language == "python":
        EXTENSION = re.compile(r"\.py$|\.pyi$")
        LANGUAGE = "python"
    elif language == "java":
        EXTENSION = re.compile(".java$")
        LANGUAGE = "java"
    elif language == "javascript":
        EXTENSION = re.compile(".js$")
        LANGUAGE = "javascript"


def get_methods_and_classes(repo_name, repo_path):
    source_files = get_source_files(repo_name, repo_path)
    functions = {}
    for source_file in source_files:
        functions = get_functions(functions, source_file)
    classes = {}
    for func in functions:
        f = func.split(".")
        if len(f) > 1:
            classes[f[0]] = {"source_file": functions[func]["source_file"]}
    return functions, classes


def get_source_files(repo_name, repo_path):
    source_files = []
    src_dir = None
    # Only look at the top level directory in this loop
    for root, dirs, files in os.walk(repo_path):
        for dir_name in dirs:
            if dir_name.lower() == "src" or dir_name == repo_name:
                src_dir = os.path.normpath(root + "/" + dir_name)
                break
        for file in files:
            if re.search(EXTENSION, file) and "test" not in file.lower():
                source_files.append(os.path.normpath(root + "/" + file))
        break
    # If we found a src directory, loop through all the files (subdirectory too)
    if src_dir:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if root == "test":
                    break
                if re.search(EXTENSION, file) and "test" not in file.lower():
                    source_files.append(os.path.normpath(root + "/" + file))
    return source_files


# Retrieves only html <code> tags because we don't want examples
# we just want to see if there source code is reflected in the documentation,
# so we need to find the signatures in the documentation
def get_documentation_signatures(page, page_soup):
    soup = page_soup
    dts = soup.find_all("dt") + soup.find_all("code")
    signatures = []

    for description in dts:
        desc = []
        for child in description.children:
            if child.name != "a":
                desc.append(child.get_text())
        description = "".join(desc).strip()
        if "(" in description:
            signatures.append([description, page])
    return signatures


# Retrieves only html <pre> tags to get code examples
def get_documentation_examples(page, page_soup):
    soup = page_soup
    raw_examples = soup.find_all("pre")
    doc_examples = []

    for raw_example in raw_examples:
        example = raw_example.get_text()
        if "(" in example:
            doc_examples.append([example, page])
    return doc_examples


def find_params(source_file):
    functions = []
    if LANGUAGE == "python":
        functions = find_python_arguments(source_file)
    elif LANGUAGE == "java":
        functions = find_java_arguments(source_file)
    elif LANGUAGE == "javascript":
        functions = find_javascript_arguments(source_file)
    return functions


def get_functions(functions, source_file):
    function_defs = find_params(source_file)
    for function in function_defs:
        if LANGUAGE == "python":
            functions[function[0]] = {"source_file": os.path.normpath("\\".join(PurePath(source_file).parts[2:])),
                                      "req_args": function[1],
                                      "opt_args": function[2]}
        else:
            if function[0] in functions:
                functions[function[0]]["req_args"].append(function[1])
            else:
                functions[function[0]] = {"source_file": os.path.normpath("\\".join(PurePath(source_file).parts[2:])),
                                          "req_args": function[1]}
    return functions


def get_doc_examples(check_examples, doc_url, pages):
    doc_examples = []
    for page in pages:
        page_soup = pages[page]
        try:
            if check_examples:
                doc_examples.extend(get_documentation_examples(page, page_soup))
            else:
                doc_examples.extend(get_documentation_signatures(page, page_soup))
        except urllib.error.HTTPError as e:
            print(e)
            print(traceback.format_exc())
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    return doc_examples
