import sys
from typing import List, Union

from analyze_library.db_service.db_service import save_lib_overview_to_db
from analyze_library.doc_parser.doc_parser import get_all_webpages, \
    get_functions_and_classes_from_doc_api_ref, get_functions_and_classes_from_doc_examples
from analyze_library.models.Signature import Signature
from analyze_library.models.doc_code_example import DocCodeExample
from analyze_library.models.doc_page import DocPage
from analyze_library.models.lib_overview import LibraryOverview
from analyze_library.models.matched_call import MatchedCall
from analyze_library.metric_calculation.navigability.navigability import get_navigability_score
from analyze_library.signature_matcher.python_doc_api_to_example_signature_matcher import \
    match_examples_to_doc_api
from analyze_library.signature_matcher.python_src_api_to_doc_api_matcher import \
    match_doc_api_to_src_api
from analyze_library.source_parser.source_code_parser import \
    get_methods_and_classes_from_source_code
from analyze_library.source_parser.source_util import clone_repo
from analyze_library.stats.stats import get_stats_ex_per_api, get_stats_api_per_example, \
    write_stats_to_file, write_doc_api_to_csv, write_examples_to_csv, get_stats_ex_per_methods_and_classes
from analyze_library.metric_calculation.text_readability.text_readability import get_text_readability
from analyze_library.metric_calculation.metrics import Metrics

depth_map = {
    'requests': 2,
    'pandas': 3,
    'graphql compiler': 3,
    'collections': 0,
    'flask': 2,
    'nltk': 2,
    'numba': 1,
    'numpy': 3,
    'gitpython': 2,
    'pyppeteer': 1,
    'python-socketio': 1,
    'scanpy': 2,
    'bionumpy': 1,
    'wikidata': 1
}


def analyze_library(language, library_name, doc_url, gh_url):
    depth = get_depth(library_name)
    # os.chdir(ROOT_DIR)

    repo_path = clone_repo(gh_url, True)
    # repo_path = 'cloned_repos/' + library_name.strip()
    print("Done cloning")

    mapped_source_api: dict[str, List[Signature]] = get_methods_and_classes_from_source_code(
        repo_name=library_name, repo_path=repo_path)

    doc_pages: List[DocPage] = get_all_webpages(doc_url, depth)

    doc_apis: List[Union[Signature, None]] = get_functions_and_classes_from_doc_api_ref(doc_pages)

    matched_signatures, unmatched_signatures = match_doc_api_to_src_api(library_name, mapped_source_api,
                                                                        doc_apis=doc_apis)

    doc_code_examples: List[DocCodeExample] = get_functions_and_classes_from_doc_examples(doc_pages)

    matched_methods: List[MatchedCall] = match_examples_to_doc_api(library_name, doc_code_examples, doc_apis)

    stats_example_per_api = get_stats_ex_per_api(doc_apis, matched_methods)
    stats_example_per_method, stats_example_per_class = get_stats_ex_per_methods_and_classes(doc_apis, matched_methods)

    stats_api_per_example = get_stats_api_per_example(matched_methods, doc_code_examples)

    # write_stats_to_file(doc_code_examples, stats_example_per_api, stats_api_per_example, library_name)
    # write_doc_api_to_csv(doc_apis, library_name)
    # write_examples_to_csv(doc_code_examples, library_name)

    print(f'Done analyzing {library_name}')


def get_depth(lib_name):
    lib_name = lib_name.lower()
    if lib_name in depth_map:
        return depth_map[lib_name]
    else:
        return 2


if __name__ == '__main__':
    analyze_library("python", "requests",
                    "https://requests.readthedocs.io/en/latest/",
                    "https://github.com/psf/requests.git")

    # analyze_library("python", "ibis",
    #                 "https://ibis-project.org/",
    #                 "https://github.com/ibis-project/ibis")

    # analyze_library("python", "pandas",
    #               "https://pandas.pydata.org/docs/reference/api/pandas.Series.plot.html",
    #               "https://github.com/pandas-dev/pandas", 0)
    #
    # analyze_library("python", "GraphQL compiler",
    #               "https://graphql-compiler.readthedocs.io/",
    #               "https://github.com/kensho-technologies/graphql-compiler", 3)
    #
    # analyze_library("python", "collections",
    #               "https://docs.python.org/3/library/collections.html",
    #               "https://github.com/python/cpython/tree/3.11/Lib/collections", 0)
    #
    # analyze_library("python", "TensorFlow",
    #               "https://www.tensorflow.org/api_docs/python/tf/all_symbols",
    #               "https://github.com/tensorflow/docs.git", 1)
    #
    # analyze_library("python", "Flask",
    #                 "https://flask.palletsprojects.com/en/3.0.x/",
    #                 "https://github.com/pallets/flask")
    # print('done flask')
    #
    # analyze_library("python", "nltk",
    #                 "https://www.nltk.org/",
    #                 "https://github.com/nltk/nltk.git")
    #
    # print('done nltk')
    #
    # analyze_library("python", "Numba",
    #                 "https://numba.readthedocs.io",
    #                 "https://github.com/numba/numba.git")
    #
    # print('done Numba')
    #
    # analyze_library("python", "numpy",
    #                 "https://numpy.org/doc/stable/",
    #                 "https://github.com/numpy/numpy.git")
    #
    # print('done numpy')
    #
    # analyze_library("python", "pandas",
    #                 "https://pandas.pydata.org/docs/",
    #                 "https://github.com/pandas-dev/pandas")
    # print('done pandas')
    #
    # analyze_library("python", "pyppeteer",
    #                 "https://pyppeteer.github.io/pyppeteer/",
    #                 "https://github.com/pyppeteer")
    #
    # print('done pyppeteer')
    #
    # analyze_library("python", "python-socketio",
    #                 "https://python-socketio.readthedocs.io/en/latest/",
    #                 "https://github.com/miguelgrinberg/python-socketio")
    #
    # print('done python-socketio')
    #
    # analyze_library("python", "scanpy",
    #                 "https://scanpy.readthedocs.io/en/stable/",
    #                 "https://github.com/scverse/scanpy")
    #
    # print('done scanpy')
    #
    # analyze_library("python", "bionumpy",
    #                 "https://scanpy.readthedocs.io/en/stable/",
    #                 "https://github.com/scverse/scanpy")
    #
    # print('done bionumpy')
    #
    # analyze_library("python", "Wikidata",
    #                 "'https://wikidata.readthedocs.io/en/stable/",
    #                 "https://github.com/dahlia/wikidata.git")
    #
    # print('done Wikidata')
    #
    # analyze_library("python", "pytest",
    #                 "https://docs.pytest.org/en/7.2.x/",
    #                 "https://github.com/pytest-dev/pytest")
    #
    # print('done pytest')

    pass
