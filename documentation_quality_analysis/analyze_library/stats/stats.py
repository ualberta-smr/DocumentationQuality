import collections
from typing import List

from analyze_library.models.class_constructor_signature import ClassConstructorSignature
from analyze_library.models.doc_code_example import DocCodeExample
from analyze_library.models.matched_call import MatchedCall
from analyze_library.models.method_signature import MethodSignature


def write_doc_api_to_csv(doc_apis, lib_name):
    names = [x.fully_qualified_name for x in doc_apis if x]
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


def get_stats_ex_per_api(doc_apis, matched_methods):
    map_of_matched_obj = {}
    for api in doc_apis:
        if api:
            map_of_matched_obj[api.fully_qualified_name] = []

    for mm in matched_methods:
        method = mm.called_signature
        if method.fully_qualified_name in map_of_matched_obj:
            map_of_matched_obj[method.fully_qualified_name].append(mm)

    return map_of_matched_obj


def get_stats_ex_per_methods_and_classes(doc_apis, matched_apis):
    matched_methods = [i for i in matched_apis if type(i.called_signature) == MethodSignature]
    matched_classes = [i for i in matched_apis if type(i.called_signature) == ClassConstructorSignature]

    map_of_matched_method = {}
    for api in doc_apis:
        if api and type(api) == MethodSignature:
            map_of_matched_method[api.fully_qualified_name] = []

    for mm in matched_methods:
        method = mm.called_signature
        if method.fully_qualified_name in map_of_matched_method:
            map_of_matched_method[method.fully_qualified_name].append(mm)

    map_of_matched_classes = {}
    for api in doc_apis:
        if api and type(api) == ClassConstructorSignature:
            map_of_matched_classes[api.fully_qualified_name] = []

    for mm in matched_classes:
        method = mm.called_signature
        if method.fully_qualified_name in map_of_matched_classes:
            map_of_matched_classes[method.fully_qualified_name].append(mm)

    return map_of_matched_method, map_of_matched_classes


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
