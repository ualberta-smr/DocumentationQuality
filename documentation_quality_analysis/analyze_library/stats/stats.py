import collections
import csv
import os
from typing import List

from analyze_library.models.class_constructor_signature import ClassConstructorSignature
from analyze_library.models.doc_code_example import DocCodeExample
from analyze_library.models.matched_call import MatchedCall
from analyze_library.models.method_signature import MethodSignature

CWD = os.getcwd()
STAT_PATH = os.path.join(CWD, "stats")


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


def write_api_per_example_stats_to_file(stats_api_per_example, lib_name):
    final_list = []
    for i in stats_api_per_example:
        stat: List[MatchedCall] = stats_api_per_example[i]

        if not stat:
            continue

        called_signatures = ""
        for matched_call in stat:
            called_signature = matched_call.called_signature.fully_qualified_name
            called_signatures = called_signatures + " " + called_signature

        apis_per_eg_list = [stat[0].raw_example.example, stat[0].url, called_signatures]

        final_list.append(apis_per_eg_list)

    with open(os.path.join(STAT_PATH, f"stats_api_per_example_{lib_name}.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(final_list)

    # api_per_example = ["ID: " + str(x) + " --> " + str(len(stats_api_per_example[x])) + "\n" +
    #                    doc_code_examples[x].example + "\n" + "---->   " +
    #                    '; '.join([i.called_signature.fully_qualified_name for i in stats_api_per_example[x]]) + "\n" for
    #                    x in
    #                    stats_api_per_example]
    # with open("stats_api_per_example_" + lib_name + ".txt", "w") as f:
    #     for i in api_per_example:
    #         f.write(i)
    #         f.write("\n")
    #         f.write("--------------------------------------")
    #         f.write("\n")


def write_examples_per_api_stats_to_file(stats_example_per_api, lib_name):
    example_per_api = [x + ": " + str(len(stats_example_per_api[x])) for x in stats_example_per_api if x]
    with open("stats_example_per_api_" + lib_name + ".csv", "w") as f:
        for i in example_per_api:
            f.write(str(i))
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
