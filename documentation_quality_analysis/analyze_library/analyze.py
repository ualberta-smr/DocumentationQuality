import collections
from typing import List, Union

from documentation_quality_analysis.analyze_library.doc_parser.doc_parser import get_all_webpages, \
    get_functions_and_classes_from_doc_api_ref, get_functions_and_classes_from_doc_examples
from documentation_quality_analysis.analyze_library.models.Signature import Signature
from documentation_quality_analysis.analyze_library.models.doc_code_example import DocCodeExample
from documentation_quality_analysis.analyze_library.models.doc_page import DocPage
from documentation_quality_analysis.analyze_library.models.matched_call import MatchedCall
from documentation_quality_analysis.analyze_library.signature_matcher.python_signature_matcher import \
    python_match_examples


def debug_metrics(language, library_name, doc_url, gh_url, depth):
    # os.chdir(ROOT_DIR)

    # repo_path = clone_repo(gh_url, True)
    # print("Done cloning")

    # get_functions_and_classes_from_src()

    doc_pages: List[DocPage] = get_all_webpages(doc_url, depth)

    doc_api: List[Union[Signature, None]] = get_functions_and_classes_from_doc_api_ref(doc_pages)

    doc_code_examples: List[DocCodeExample] = get_functions_and_classes_from_doc_examples(doc_pages)

    matched_methods: List[MatchedCall] = python_match_examples(library_name, doc_code_examples, doc_api)

    stats_example_per_api = get_stats_ex_per_api(doc_api, matched_methods)

    stats_api_per_example = get_stats_api_per_example(matched_methods, doc_code_examples)

    # write_stats_to_file(doc_code_examples, stats_example_per_api, stats_api_per_example, library_name)

    print("done")

    # write_doc_api_to_csv(doc_api)
    # write_examples_to_csv(doc_code_examples)


def write_doc_api_to_csv(doc_api, lib_name):
    names = [x.fully_qualified_name for x in doc_api if x]
    with open("stats/" + lib_name + "_all_doc_api.csv", "w") as f:
        for i in names:
            f.write(str(i))
            f.write("\n")


def write_examples_to_csv(doc_code_examples, lib_name):
    examples = ["ID: " + str(x.id) + " --> \n" + x.example for x in doc_code_examples if x]
    with open("stats/" + lib_name + "_all_code_examples.csv", "w") as f:
        for i in examples:
            f.write(str(i))
            f.write("\n")
            f.write(";")
            f.write("\n")


def write_stats_to_file(doc_code_examples, stats_example_per_api, stats_api_per_example, lib_name):
    example_per_api = [x + ": " + str(len(stats_example_per_api[x])) for x in stats_example_per_api if
                       len(stats_example_per_api[x]) > 0]
    with open("temp_stats_example_per_api_" + lib_name + ".txt", "w") as f:
        for i in example_per_api:
            f.write(str(i))
            f.write("\n")

    api_per_example = ["ID: " + str(x) + " --> " + str(len(stats_api_per_example[x])) + "\n" +
                       doc_code_examples[x].example + "\n" + "---->   " +
                       '; '.join([i.called_signature.fully_qualified_name for i in stats_api_per_example[x]]) + "\n" for
                       x in
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
        method = mm.called_signature
        if method.fully_qualified_name in map_of_matched_obj:
            map_of_matched_obj[method.fully_qualified_name].append(mm)

    return map_of_matched_obj


def get_stats_api_per_example(matched_methods: List[MatchedCall], doc_code_examples: List[DocCodeExample]):
    map_of_examples_to_api = {}

    for mm in matched_methods:
        example = mm.raw_example

        if example.id in map_of_examples_to_api:
            map_of_examples_to_api[example.id].append(mm)
        else:
            map_of_examples_to_api[example.id] = [mm]

    for eg in doc_code_examples:
        if eg.id not in map_of_examples_to_api:
            map_of_examples_to_api[eg.id] = []

    return collections.OrderedDict(sorted(map_of_examples_to_api.items()))


if __name__ == '__main__':
    # debug_metrics("python", "requests",
    #               "https://requests.readthedocs.io/en/latest/api/",
    #               "https://github.com/psf/requests.git", 0)

    debug_metrics("python", "pandas",
                  "https://pandas.pydata.org/docs/reference/api/pandas.Series.__array__.html",
                  "https://github.com/pandas-dev/pandas", 0)

    # debug_metrics("python", "pandas",
    #               "https://pandas.pydata.org/docs/reference/api/pandas.Series.plot.html",
    #               "https://github.com/pandas-dev/pandas", 0)

    # debug_metrics("python", "GraphQL compiler",
    #               "https://graphql-compiler.readthedocs.io/",
    #               "https://github.com/kensho-technologies/graphql-compiler", 3)

    # debug_metrics("python", "collections",
    #               "https://docs.python.org/3/library/collections.html",
    #               "https://github.com/python/cpython/tree/3.11/Lib/collections", 0)

    # debug_metrics("python", "TensorFlow",
    #               "https://www.tensorflow.org/api_docs/python/tf/all_symbols",
    #               "https://github.com/tensorflow/docs.git", 1)


