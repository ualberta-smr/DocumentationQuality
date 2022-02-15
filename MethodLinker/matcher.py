import html
import re
import os
import csv

from MethodLinker.python_matcher import find_python_arguments
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


def find_params(language, source_file):
    functions = []
    if language == "python":
        functions = find_python_arguments(source_file)
    return functions


def get_methods_and_classes(language, repo_url):
    source_files = get_source_files(repo_url)
    methods = {}
    for source_file in source_files:
        funcs = find_params(language, source_file)
        for func in funcs:
            methods[func[0]] = {"source_file": source_file,
                                  "req_args": func[1][0],
                                  "opt_args": func[1][1]}
    classes = {}
    for meth in methods:
        f = meth.split(".")
        if len(f) > 1:
            classes[f[0]] = {"source_file": methods[meth]["source_file"]}

    return methods, classes


def calculate_ratios(language, repo_name, repo_url, doc_url, pages):
    extension_finder(language)
    methods, classes = get_methods_and_classes(language, repo_url)
    doc_examples = []
    for page in pages:
        try:
            doc_examples.extend(get_documentation_examples(doc_url, page))
        except:
            pass

    call_regex = re.compile(r"(?:\w+\.)?\w+(?=\()")
    method_calls = set()
    with open("results/" + repo_name + ".csv", "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Example", "Method", "Function", "Source", "Matched"])
        for i, ex in enumerate(doc_examples):
            example = ex[0]
            calls = re.findall(call_regex, example)
            for call in calls:
                func_def = None
                method = call.split("(")[0].lower()
                if method not in methods:
                    function_split = method.split(".")
                    if len(function_split) > 1:
                        if function_split[1] in methods:
                            func_def = methods[function_split[1]]
                else:
                    func_def = methods[method]
                if func_def:
                    args_regex = re.compile(r"(?<=%s\()(?:.|\n)+?(?=\))" % method)
                    args = re.search(args_regex, example)
                    try:
                        num_args = len(args[0].split(", "))
                    except TypeError:
                        num_args = 0
                    if func_def["req_args"] <= num_args <= (func_def["req_args"] + func_def["opt_args"]):
                        method_calls.add((func_def["source_file"], method))
                        writer.writerow([example, call, method, func_def["source_file"], "True"])
                    else:
                        writer.writerow([example, call, method, func_def["source_file"], "False"])
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

    total_classes = len(classes)
    total_methods = len(methods)
    return example_count, total_methods, classes_count, total_classes
