import os
import csv


def evaluate_links(truth_file, test_file):
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
            with open(os.path.normpath("comparison/" + truth_file.split("\\")[1]), "w", encoding="utf-8", newline="") as results:
                result_writer = csv.writer(results, quoting=csv.QUOTE_MINIMAL)
                result_writer.writerow(["Example", "Truth functions", "Test functions", "Linked functions", "Source"])
                truth_headers = ["example", "page", "class", "function", "source"]
                test_headers = ["example", "extracted", "linked", "source", "matched"]

                truth_dict = dict()
                for row1 in truth_list:
                    truth_row = dict(zip(truth_headers, row1))
                    if truth_row["example"] in truth_dict:
                        truth_dict[truth_row["example"]].append((truth_row["class"], truth_row["function"], truth_row["source"]))
                    else:
                        truth_dict[truth_row["example"]] = [(truth_row["class"], truth_row["function"], truth_row["source"])]
                test_dict = dict()
                for row2 in test_list:
                    test_row = dict(zip(test_headers, row2))
                    if test_row["example"] in test_dict:
                        links = test_row["linked"].split("\n")
                        for link in links:
                            test_dict[test_row["example"]].append((test_row["extracted"], link, test_row["source"]))
                    else:
                        links = test_row["linked"].split("\n")
                        if len(links) > 1:
                            test_dict[test_row["example"]] = [(test_row["extracted"], links[0], test_row["source"])]
                            for link in links:
                                test_dict[test_row["example"]].append([(test_row["extracted"], link, test_row["source"])])
                        else:
                            test_dict[test_row["example"]] = [(test_row["extracted"], links[0], test_row["source"])]

                for key, values in truth_dict.items():
                    truth_functions = []
                    test_functions = []
                    linked_functions = []
                    if key in test_dict:
                        test_values = test_dict[key]
                        for value in values:
                            truth_functions.append(value[1])
                        for test_value in test_values:
                            test_functions.append(test_value[1])
                        for value in values:
                            for test_value in test_values:
                                if value[1] == test_value[1].split(".")[-1] and os.path.normpath(value[2]) == os.path.normpath(test_value[2]):
                                    linked_functions.append(test_value[1])
                                    correct += 1
                                    break
                        result_writer.writerow([key, truth_functions, test_functions, linked_functions])
    return [correct, len(test_list), correct / len(test_list),  # Precision
            correct, len(truth_list), correct / len(truth_list)]  # Recall


if __name__ == '__main__':
    with open(os.path.normpath("comparison/evaluation.csv"), "w",
              encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["Repo", "Correct", "Total test", "Precision", "Correct",
             "Total truth", "Recall"])
        # file1 = "truth\\CoreNLP.csv"
        # file2 = "results\\CoreNLP.csv"
        # writer.writerow([file1.split("\\")[1].split(".")[0],
        #                  *evaluate_links(file1, file2)])
        for file1 in os.listdir("truth"):
            truth_file = os.path.join("truth", file1)
            for file2 in os.listdir("results"):
                test_file = os.path.join("results", file2)
                if file1 == file2:
                    writer.writerow([file1.split(".")[0],
                                     *evaluate_links(truth_file, test_file)])
                    break
