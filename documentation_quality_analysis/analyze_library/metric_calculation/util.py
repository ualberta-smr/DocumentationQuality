def get_percentage_api_with_code_example(stats_example_per_api):
    try:
        number_of_apis = len([api for api in stats_example_per_api if api])
        number_of_apis_with_example = len([eg for eg in stats_example_per_api if len(stats_example_per_api[eg]) > 0])

        return round((number_of_apis_with_example / number_of_apis) * 100)
    except ZeroDivisionError:
        return 0


def get_percentage_of_doc_api_in_src_code(doc_apis, matched_signatures):
    try:
        number_of_apis = len([api for api in doc_apis if api.name])
        number_of_matched_api = len(matched_signatures)

        return round((number_of_matched_api / number_of_apis) * 100)
    except ZeroDivisionError:
        return 0


def get_no_of_apis_with_example(stats_example_per_api):
    number_of_apis_with_example = len([eg for eg in stats_example_per_api if len(stats_example_per_api[eg]) > 0])

    return number_of_apis_with_example


def get_no_of_doc_api(doc_apis):
    return len([api for api in doc_apis if api.name])