from typing import List, Union

from DocumentationQualityAnalysis.analyze_library.doc_parser.doc_parser import get_all_webpages, \
    get_functions_and_classes_from_doc_api_ref, get_functions_and_classes_from_doc_examples
from DocumentationQualityAnalysis.analyze_library.models.class_constructor_signature import ClassConstructorSignature
from DocumentationQualityAnalysis.analyze_library.models.doc_page import DocPage
from DocumentationQualityAnalysis.analyze_library.models.method_signature import MethodSignature
from DocumentationQualityAnalysis.analyze_library.signature_matcher.python_signature_matcher import \
    python_match_examples
from Summary.analyze.util import clone_repo


def debug_metrics(language, library_name, doc_url, gh_url):
    # os.chdir(ROOT_DIR)

    repo_path = clone_repo(gh_url, True)
    print("Done cloning")

    # get_functions_and_classes_from_src()

    doc_pages: List[DocPage] = get_all_webpages(doc_url, 2)

    doc_api: List[Union[MethodSignature, ClassConstructorSignature, None]] = get_functions_and_classes_from_doc_api_ref(
        doc_pages)

    doc_code_examples: List = get_functions_and_classes_from_doc_examples(doc_pages)

    matched_methods = python_match_examples(library_name, doc_code_examples, doc_api)

    stats = get_stats(doc_api, matched_methods)

    print([s + ":  " + str(len(stats[s])) for s in stats])


def get_stats(doc_api, matched_methods):
    map_of_matched_obj = {}
    for api in doc_api:
        if api:
            map_of_matched_obj[api.fully_qualified_name] = []

    for mm in matched_methods:
        method = mm.method
        if method.fully_qualified_name in map_of_matched_obj:
            map_of_matched_obj[method.fully_qualified_name].append(mm)

    return map_of_matched_obj


if __name__ == '__main__':
    debug_metrics("python", "requests",
                  "https://requests.readthedocs.io/en/latest/api/",
                  "https://github.com/psf/requests.git")
