import os

from MethodLinker.matcher import calculate_ratios
from util import get_webpages, add_or_update_method_record


def api_methods_examples(language, library_name, doc_url, repo_url,
                         check_examples):
    os.chdir("MethodLinker")
    pages = get_webpages(doc_url, library_name)
    example_count, total_methods, classes_count, total_classes = calculate_ratios(
        language, library_name, repo_url, doc_url, pages, check_examples)
    add_or_update_method_record("overview_library",
                                {"library_name": "'" + library_name + "'",
                                 "gh_url": "'" + repo_url + "'",
                                 "doc_url": "'" + doc_url + "'",
                                 "num_method_examples": example_count,
                                 "num_methods": total_methods,
                                 "num_class_examples": classes_count,
                                 "num_classes": total_classes})
    # print("Methods found w/ examples:", example_count)
    # print("Total methods:", total_methods)
    # print("Classes found w/ examples:", classes_count)
    # print("Total classes:", total_classes)
    # if total_methods > 0:
    #     print(example_count / total_methods)
    # if total_classes > 0:
    #     print(classes_count / total_classes)
    os.chdir("..")
