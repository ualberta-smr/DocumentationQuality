from .matcher import calculate_ratios
from ..util import get_webpages


def api_methods_examples(language, library_name, doc_url, repo_path, check_examples):
    pages = get_webpages(doc_url, library_name)
    example_count, total_methods, classes_count, total_classes = calculate_ratios(
        language, library_name, repo_path, doc_url, pages, check_examples)
    return example_count, total_methods, classes_count, total_classes
    # print("Methods found w/ examples:", example_count)
    # print("Total methods:", total_methods)
    # print("Classes found w/ examples:", classes_count)
    # print("Total classes:", total_classes)
    # if total_methods > 0:
    #     print(example_count / total_methods)
    # if total_classes > 0:
    #     print(classes_count / total_classes)
