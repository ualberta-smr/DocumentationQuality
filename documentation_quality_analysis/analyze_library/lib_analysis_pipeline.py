import pandas as pd

from analyze_library.lib_analysis_service import analyze_library
from analyze_library.prioritize_api.heurictics.has_api_analysis import find_SO_posts_for_APIs_wo_eg
from analyze_library.prioritize_api.llm.discusses_api_pipeline import analyze_post_discusses_api
from analyze_library.stack_overflow_service.stack_overflow_service import get_SO_posts, SO_TAGS


def get_apis_without_eg():
    analyze_library(library_name=lib_name,
                    language=lib_map[lib_name]['language'],
                    doc_url=lib_map[lib_name]['doc_url'],
                    gh_url=lib_map[lib_name]['gh_url']
                    )


if __name__ == '__main__':
    lib_name = 'scipy'

    lib_map = {
        'scipy': {
            'language': 'python',
            'doc_url': "https://docs.scipy.org/doc/scipy/index.html",
            'gh_url': "https://github.com/scipy/scipy",
            'SO_tags': SO_TAGS['scipy']
        },
        'numpy': {
            'language': 'python',
            'doc_url': "https://numpy.org/doc/stable/",
            'gh_url': "https://github.com/numpy/numpy.git",
            'SO_tags': SO_TAGS['numpy']
        },
        'pandas': {
            'language': 'python',
            'doc_url': "https://pandas.pydata.org/docs/",
            'gh_url': "https://github.com/pandas-dev/pandas",
            'SO_tags': 'python;pandas'
        },
        'requests': {
            'language': 'python',
            'doc_url': 'https://requests.readthedocs.io/en/latest/',
            'gh_url': 'https://github.com/psf/requests.git',
            'SO_tags': ''
        },
        'boto3': {
            'language': 'python',
            'doc_url': 'https://boto3.amazonaws.com/v1/documentation/api/latest/index.html',
            'gh_url': 'https://github.com/boto/boto3',
            'SO_tags': 'python;boto3'

        },
        'botocore': {
            'language': 'python',
            'doc_url': 'https://botocore.amazonaws.com/v1/documentation/api/latest/index.html',
            'gh_url': 'https://github.com/boto/botocore',
            'SO_tags': 'python;botocore'

        },
        'dagster': {
            'language': 'python',
            'doc_url': 'https://docs.dagster.io/getting-started',
            'gh_url': 'https://github.com/dagster-io/dagster',
            'SO_tags': 'dagster'
        },
        'urllib3': {
            'language': 'python',
            'doc_url': 'https://urllib3.readthedocs.io/en/stable/index.html',
            'gh_url': 'https://github.com/urllib3/urllib3',
            'SO_tags': 'python;urllib3'
        },
        'typing_extensions': {
            'language': 'python',
            'doc_url': "https://typing-extensions.readthedocs.io/en/latest/",
            'gh_url': "https://github.com/python/typing_extensions",
            'SO_tags': SO_TAGS['typing_extensions']
        },
        'opencensus': {
            'language': 'python',
            'doc_url': "https://opencensus.io/api/python/trace/usage.html",
            'gh_url': "https://github.com/census-instrumentation/opencensus-python/",
            'SO_tags': SO_TAGS['opencensus']
        },
        'fn_graph': {
            'language': 'python',
            'doc_url': "https://fn-graph.readthedocs.io/en/latest/index.html",
            'gh_url': "https://github.com/BusinessOptics/fn_graph",
            'SO_tags': SO_TAGS['fn_graph']
        },
        'charset_normalizer': {
            'language': 'python',
            'doc_url': "https://charset-normalizer.readthedocs.io/en/latest/index.html",
            'gh_url': "https://github.com/Ousret/charset_normalizer",
            'SO_tags': SO_TAGS['fn_graph']
        },
        'desert': {
            'language': 'python',
            'doc_url': "https://desert.readthedocs.io/en/stable/",
            'gh_url': "https://github.com/python-desert/desert",
            'SO_tags': SO_TAGS['fn_graph']
        },
    }

    # get_apis_without_eg()

    # file_path = get_SO_posts(lib_name=lib_name)
    #
    find_SO_posts_for_APIs_wo_eg(lib_name=lib_name)

    analyze_post_discusses_api(lib_name=lib_name)


