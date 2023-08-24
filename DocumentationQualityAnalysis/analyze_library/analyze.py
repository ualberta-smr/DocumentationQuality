from typing import List, Union

from DocumentationQualityAnalysis.analyze_library.doc_parser.doc_parser import get_all_webpages, \
    get_functions_and_classes_from_doc_api_ref, get_functions_and_classes_from_doc_examples
from DocumentationQualityAnalysis.analyze_library.models.Signature import Signature
from DocumentationQualityAnalysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from DocumentationQualityAnalysis.analyze_library.models.doc_code_example import DocCodeExample
from DocumentationQualityAnalysis.analyze_library.models.doc_page import DocPage
from DocumentationQualityAnalysis.analyze_library.models.matched_function import MatchedFunction
from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature
from DocumentationQualityAnalysis.analyze_library.signature_matcher.python_signature_matcher import \
    python_match_examples
from Summary.analyze.util import clone_repo


def debug_metrics(language, library_name, doc_url, gh_url):
    # os.chdir(ROOT_DIR)

    # repo_path = clone_repo(gh_url, True)
    # print("Done cloning")

    # get_functions_and_classes_from_src()

    doc_pages: List[DocPage] = get_all_webpages(doc_url, 3)

    doc_api: List[Union[Signature, None]] = get_functions_and_classes_from_doc_api_ref(doc_pages)

    doc_code_examples: List[DocCodeExample] = get_functions_and_classes_from_doc_examples(doc_pages)

    matched_methods: List[MatchedFunction] = python_match_examples(library_name, doc_code_examples, doc_api)

    write_stats_to_file(doc_api, doc_code_examples, matched_methods, library_name)

    print("done")


def write_stats_to_file(doc_api, doc_code_examples, matched_methods, lib_name):
    stats_example_per_api = get_stats_ex_per_api(doc_api, matched_methods)

    example_per_api = [x + ": " + str(len(stats_example_per_api[x])) for x in stats_example_per_api if
                       len(stats_example_per_api[x]) > 0]
    with open("temp_stats_example_per_api_" + lib_name + ".txt", "w") as f:
        for i in example_per_api:
            f.write(str(i))
            f.write("\n")

    stats_api_per_example = get_stats_api_per_example(matched_methods)

    api_per_example = ["ID: " + str(x) + " --> " + str(len(stats_api_per_example[x])) + "\n" +
                       doc_code_examples[x].example + "\n" + "---->   " +
                       '; '.join([i.method.fully_qualified_name for i in stats_api_per_example[x]]) + "\n" for x in
                       stats_api_per_example]
    with open("temp_stats_api_per_example_" + lib_name + ".txt", "w") as f:
        for i in api_per_example:
            f.write(i)
            f.write("\n")
            f.write("--------------------------------------")
            f.write("\n")


def get_stats_ex_per_api(doc_api, matched_methods):
    map_of_matched_obj = {}
    for api in doc_api:
        if api:
            map_of_matched_obj[api.fully_qualified_name] = []

    for mm in matched_methods:
        method = mm.method
        if method.fully_qualified_name in map_of_matched_obj:
            map_of_matched_obj[method.fully_qualified_name].append(mm)

    return map_of_matched_obj


def get_stats_api_per_example(matched_methods: List[MatchedFunction]):
    map_of_examples_to_api = {}

    for mm in matched_methods:
        example = mm.raw_example

        if example.id in map_of_examples_to_api:
            map_of_examples_to_api[example.id].append(mm)
        else:
            map_of_examples_to_api[example.id] = [mm]

    return map_of_examples_to_api


if __name__ == '__main__':
    debug_metrics("python", "requests",
                  "https://requests.readthedocs.io/en/latest/api/",
                  "https://github.com/psf/requests.git")

    # debug_metrics("python", "pandas",
    #               "https://pandas.pydata.org/docs/index.html",
    #               "https://github.com/pandas-dev/pandas")
