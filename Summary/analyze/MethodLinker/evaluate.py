import os
import csv
import ast
import re


def evaluate_signature_links(truth_file, test_file):
    with open(truth_file, "r", encoding="utf-8") as temp:
        reader = csv.reader(temp)
        next(reader, None)
        truth_list = list(reader)
        with open(test_file, "r", encoding="utf-8") as temp:
            reader = csv.reader(temp)
            next(reader, None)
            test_list = list(reader)
            correct = 0
            with open(os.path.normpath("comparison/signatures/" + truth_file.split("\\")[-1]), "w", encoding="utf-8", newline="") as results:
                result_writer = csv.writer(results, quoting=csv.QUOTE_MINIMAL)
                result_writer.writerow(["Example", "Signature", "Extracted", "Linked"])
                truth_headers = ["code", "signature", "linked", "page"]
                test_headers = ["example", "extracted", "linked", "page", "matched"]
                truth_dict = dict()
                for row1 in truth_list:
                    truth_row = dict(zip(truth_headers, row1))
                    if truth_row["code"].strip() in truth_dict:
                        truth_dict[truth_row["code"].strip()].append((truth_row["signature"], truth_row["linked"], truth_row["page"]))
                    else:
                        truth_dict[truth_row["code"].strip()] = [(truth_row["signature"], truth_row["linked"], truth_row["page"])]

                test_dict = dict()
                for row2 in test_list:
                    test_row = dict(zip(test_headers, row2))
                    try:
                        ext = ast.literal_eval(test_row["extracted"])
                    except:
                        ext = test_row["extracted"]
                    try:
                        temp = ast.literal_eval(test_row["linked"])
                        if len(temp) > 2:
                            print(test_row["linked"])
                        tup = temp
                        if isinstance(temp, tuple):
                            try:
                                temp1 = ast.literal_eval(temp[0])
                            except:
                                temp1 = temp[0]
                            try:
                                temp2 = ast.literal_eval(temp[1])
                            except:
                                temp2 = temp[1]
                            tup = (temp1, temp2)
                    except ValueError:
                        tup = test_row["linked"].split(",")
                    if test_row["example"].strip() in test_dict:
                        test_dict[test_row["example"]].append((ext, tup, test_row["page"]))
                    else:
                        test_dict[test_row["example"]] = [(ext, tup, test_row["page"])]

                total_truth_functions = 0
                total_test_functions = 0
                for key, values in truth_dict.items():
                    truth_functions = []
                    test_functions = []
                    linked_functions = []
                    if key in test_dict:
                        for value in values:
                            truth_functions.append(value[0])
                        total_truth_functions += len(truth_functions)

                        test_values = test_dict[key]
                        for test_value in test_values:
                            if test_value[-1] == "N/A":
                                test_functions.append((test_value[0], test_value[1]))
                            else:
                                test_functions.append(test_value[1])
                        total_test_functions += len(test_functions)

                        param_regex = re.compile("(?<=\().*(?=\))")
                        for value in values:
                            for test_value in test_values:
                                if os.path.normpath(value[-1]) == os.path.normpath(test_value[-1]):
                                    truth_params = re.findall(param_regex, value[1])[0]
                                    truth_params = truth_params.split(", ") if truth_params else []
                                    if isinstance(test_value[1][1], list):
                                        if not any(isinstance(signature, list) for signature in test_value[1][1]):
                                            if value[1].split("(")[0] == test_value[1][0] and set(truth_params) == set(test_value[1][1]):
                                                linked_functions.append(test_value[1])
                                                correct += 1
                                                break

                        result_writer.writerow([key, truth_functions, test_functions, linked_functions])
    return [correct, total_test_functions, correct / total_test_functions if total_test_functions else 0,  # Precision
            correct, total_truth_functions, correct / total_truth_functions if total_truth_functions else 0]  # Recall


def evaluate_example_links(truth_file, test_file):
    with open(truth_file, "r", encoding="utf-8") as temp:
        reader = csv.reader(temp)
        # Skip over the header
        next(reader, None)
        truth_list = list(reader)
        with open(test_file, "r", encoding="utf-8") as temp:
            reader = csv.reader(temp)
            next(reader, None)
            test_list = list(reader)
            correct = 0
            with open(os.path.normpath("comparison/examples/" + truth_file.split("\\")[-1]), "w", encoding="utf-8", newline="") as results:
                result_writer = csv.writer(results, quoting=csv.QUOTE_MINIMAL)
                result_writer.writerow(["Example", "Truth functions", "Test functions", "Linked functions"])
                truth_headers = ["example", "page", "class", "function", "source"]
                test_headers = ["example", "extracted", "linked", "source", "matched"]

                truth_dict = dict()
                for row1 in truth_list:
                    truth_row = dict(zip(truth_headers, row1))
                    if truth_row["example"].strip() in truth_dict:
                        truth_dict[truth_row["example"].strip()].append((truth_row["class"], truth_row["function"] if truth_row["function"] != "N/A" else "", truth_row["source"]))
                    else:
                        truth_dict[truth_row["example"].strip()] = [(truth_row["class"], truth_row["function"] if truth_row["function"] != "N/A" else "", truth_row["source"])]
                test_dict = dict()
                for row2 in test_list:
                    test_row = dict(zip(test_headers, row2))
                    if test_row["example"].strip() in test_dict:
                        links = test_row["linked"].split("\n")
                        for link in links:
                            test_dict[test_row["example"].strip()].append((test_row["extracted"], link, test_row["source"]))
                    else:
                        links = test_row["linked"].split("\n")
                        if len(links) > 1:
                            test_dict[test_row["example"].strip()] = [(test_row["extracted"], links[0], test_row["source"])]
                            for link in links:
                                test_dict[test_row["example"].strip()].append([(test_row["extracted"], link, test_row["source"])])
                        else:
                            test_dict[test_row["example"].strip()] = [(test_row["extracted"], links[0], test_row["source"])]

                total_truth_functions = 0
                total_test_functions = 0
                for key, values in truth_dict.items():
                    truth_functions = []
                    test_functions = []
                    linked_functions = []
                    if key in test_dict:
                        test_values = test_dict[key]
                        for value in values:
                            truth_functions.append(value[1])
                        total_truth_functions += len(truth_functions)
                        for test_value in test_values:
                            if test_value[1] == "N/A":
                                test_functions.append((test_value[0], test_value[1]))
                            else:
                                test_functions.append(test_value[1])
                        total_test_functions += len(test_functions)
                        for value in values:
                            for test_value in test_values:
                                if value[1] == test_value[1].split(".")[-1] and os.path.normpath(value[2]) == os.path.normpath(test_value[2]):
                                    linked_functions.append(test_value[1])
                                    correct += 1
                                    break
                        result_writer.writerow([key, truth_functions, test_functions, linked_functions])
    return [correct, total_test_functions, correct / total_test_functions,  # Precision
            correct, total_truth_functions, correct / total_truth_functions]  # Recall


if __name__ == '__main__':
    if not os.path.isdir("comparison"):
        os.mkdir("comparison")
    if not os.path.isdir(os.path.normpath("comparison/examples")):
        os.mkdir(os.path.normpath("comparison/examples"))
    if not os.path.isdir(os.path.normpath("comparison/signatures")):
        os.mkdir(os.path.normpath("comparison/signatures"))

    with open(os.path.normpath("comparison/signatures/evaluation.csv"), "w",
              encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["Repo", "Correct", "Total test", "Precision", "Correct",
             "Total truth", "Recall"])
        # file1 = "truth\\qunit.csv"
        # file2 = "results\\qunit.csv"
        # writer.writerow([file1.split("\\")[1].split(".")[0], *evaluate_links(file1, file2)])
        for file1 in os.listdir("truth/signatures"):
            truth_file = os.path.normpath(os.path.join("truth/signatures/", file1))
            for file2 in os.listdir("results/signatures"):
                test_file = os.path.normpath(os.path.join("results/signatures/", file2))
                if file1 == file2:
                    writer.writerow([file1.split(".")[0],
                                     *evaluate_signature_links(truth_file, test_file)])
                    break