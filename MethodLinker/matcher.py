import html
import itertools
import os
import pprint
from shutil import rmtree
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from git import Repo

from MethodLinker.java_matcher import *
from MethodLinker.python_matcher import *
from MethodLinker.javascript_matcher import *
from util import HEADERS

EXTENSION = None
DEFAULT_VALUES = False


def extension_finder(language):
    language = language.lower().strip()
    global EXTENSION
    global DEFAULT_VALUES
    if language == "python":
        EXTENSION = ".py"
        DEFAULT_VALUES = True
    elif language == "java":
        EXTENSION = ".java"
    elif language == "javascript":
        EXTENSION = ".js"


def get_documentation_examples(doc_url, url):
    try:
        req = Request(url=url, headers=HEADERS)
    except ValueError:
        try:
            url = re.match(re.compile(".+/"), doc_url)[0] + url
            req = Request(url=url, headers=HEADERS)
        except ValueError:
            return []
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    raw_examples = soup.find_all("code") + soup.find_all("pre")
    doc_examples = []

    for raw_example in raw_examples:
        example = raw_example.get_text()
        if "(" in example:
            doc_examples.append([example, url])
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
    repo_regex = re.compile(r"(?<=/)[a-zA-Z.-]+(?!/)$")
    repo_name = re.search(repo_regex, repo_url)[0][:-4]
    if os.path.exists(repo_name):
        rmtree(repo_name, onerror=rmtree_access_error_handler)
    Repo.clone_from(repo_url, repo_name)
    source_files = []
    src_dir = None
    # Only look at the top level directory in this loop
    for root, dirs, files in os.walk(repo_name):
        for dir_name in dirs:
            if dir_name.lower() == "src" or dir_name == repo_name:
                src_dir = os.path.normpath(root + "/" + dir_name)
                break
        for file in files:
            if re.search(re.compile(EXTENSION + "$"), file) and "test" not in file.lower():
                source_files.append(os.path.normpath(root + "/" + file))
        break
    # If we found a src directory, loop through all the files (subdirectory too)
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if "test" in root:
                break
            if re.search(re.compile(EXTENSION + "$"), file) and "test" not in file.lower():
                source_files.append(os.path.normpath(root + "/" + file))
    return source_files


def find_params(source_file):
    functions = []
    if EXTENSION == ".py":
        functions = find_python_arguments(source_file)
    elif EXTENSION == ".java":
        functions = find_java_arguments(source_file)
    elif EXTENSION == ".js":
        functions = find_javascript_arguments(source_file)
    return functions


def get_functions(functions, source_file):
    function_defs = find_params(source_file)
    for function in function_defs:
        if EXTENSION == ".py":
            functions[function[0]] = {"source_file": source_file,
                                      "req_args": function[1][0],
                                      "opt_args": function[1][1]}
        else:
            if function[0] in functions:
                functions[function[0]]["req_args"].append(function[1])
            else:
                functions[function[0]] = {"source_file": source_file,
                                          "req_args": [function[1]]}
    return functions


def get_methods_and_classes(repo_url):
    os.chdir("repos")
    source_files = get_source_files(repo_url)
    functions = {}
    for source_file in source_files:
        functions = get_functions(functions, source_file)
    classes = {}
    for func in functions:
        f = func.split(".")
        if len(f) > 1:
            classes[f[0]] = {"source_file": functions[func]["source_file"]}
    os.chdir("..")
    return functions, classes


def calculate_ratios(language, repo_name, repo_url, doc_url, pages):
    extension_finder(language)
    functions, classes = get_methods_and_classes(repo_url)
    doc_examples = []
    for page in pages:
        try:
            doc_examples.extend(get_documentation_examples(doc_url, page))
        except:
            pass
    # Remove duplicates but retain order
    doc_examples = list(doc_examples for doc_examples, _ in itertools.groupby(doc_examples))
    method_calls = set()
    if EXTENSION == ".py":
        method_calls = python_match(repo_name, doc_examples, functions, classes)
    elif EXTENSION == ".java":
        method_calls = java_match(repo_name, doc_examples, functions, classes)
    elif EXTENSION == ".js":
        method_calls = javascript_match(repo_name, doc_examples, functions, classes)

    example_count = len(method_calls)
    seen_classes = set()
    for examples in method_calls:
        example = examples[1].split(".")
        if example[0] in classes:
            seen_classes.add(example[0])

    return example_count, len(functions), len(seen_classes), len(classes)
