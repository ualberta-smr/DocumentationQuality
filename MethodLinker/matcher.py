import html
import re
import os
import csv
import pprint
import itertools
import ast

from MethodLinker.python_matcher import find_python_arguments
from MethodLinker.java_matcher import find_java_arguments
from util import HEADERS
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from git import Repo
from shutil import rmtree


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
            if EXTENSION in file and "test" not in file.lower():
                source_files.append(os.path.normpath(root + "/" + file))
        break
    # If we found a src directory, loop through all the files (subdirectory too)
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if "test" in root:
                break
            if EXTENSION in file and "test" not in file.lower():
                source_files.append(os.path.normpath(root + "/" + file))
    return source_files


def find_params(source_file):
    functions = []
    if EXTENSION == ".py":
        functions = find_python_arguments(source_file)
    elif EXTENSION == ".java":
        functions = find_java_arguments(source_file)
    return functions


def get_functions(functions, source_file):
    function_defs = find_params(source_file)
    for function in function_defs:
        if EXTENSION == ".py":
            functions[function[0]] = {"source_file": source_file,
                                      "req_args": function[1][0],
                                      "opt_args": function[1][1]}
        elif EXTENSION == ".java":
            functions[function[0]] = {"source_file": source_file,
                                      "req_args": function[1]}
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
    call_regex = re.compile(r"(?:\w+\.)?\w+(?=\()")
    method_calls = set()
    with open("results/" + repo_name + ".csv", "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Example", "Extracted Function", "Linked Function", "Source File", "Linked"])
        for i, ex in enumerate(doc_examples):
            example = ex[0]
            found_calls = re.findall(call_regex, example)
            calls = []
            # Remove duplicate found calls
            [calls.append(item) for item in found_calls if item not in calls]
            for call in calls:
                func_def = None
                function = call.split("(")[0].lower()
                # Check if the function exists in our dictionary
                if function not in functions:
                    function_split = function.split(".")
                    # If not then maybe it does if we remove the first prefix
                    # e.g., nltk.nltk.get -> nltk.get
                    if len(function_split) > 1:
                        if function_split[1] in functions:
                            func_def = functions[function_split[1]]
                else:
                    func_def = functions[function]
                if func_def:
                    function_calls = re.findall(re.compile(r"%s\([a-zA-Z_:.,/\\ =(){}\'\"]*\)" % function.replace(".", "\.")), example)
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
                            method_calls.add((func_def["source_file"], function))
                            writer.writerow([example, call, function, func_def["source_file"], "True"])
                        else:
                            writer.writerow([example, call, function, func_def["source_file"], "False"])
                else:
                    potential_class = call.split(".")[-1]
                    if potential_class.lower() in classes:
                        writer.writerow([example, potential_class, "__init__", classes[potential_class.lower()]["source_file"], "True"])
                    else:
                        writer.writerow([example, call, "N/A", "N/A", "N/A"])

    example_count = len(method_calls)
    classes_count = 0
    for examples in method_calls:
        example = examples[1].split(".")
        # If we cannot split anything then the method is not in a class
        if len(example) > 1:
            if example[0].lower() in classes:
                classes_count += 1

    return example_count, len(functions), classes_count, len(classes)
