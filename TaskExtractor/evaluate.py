import csv
import os
import re
from fuzzywuzzy import fuzz


def find_longer(list_one, list_two):
    return (list_one, list_two) if len(list_one) > len(list_two) else (list_two, list_one)


def evaluate_tasks(truth, test):
    with open(truth, "r", newline="") as truth_set:
        truth_reader = csv.reader(truth_set)
        # Skip over the header
        next(truth_reader, None)
        truth_list = list(truth_reader)
        with open(test, "r", newline="") as test_set:
            test_reader = csv.reader(test_set)
            # TODO: For now there is no headers in the results csvs
            # next(test_reader, None)
            test_list = list(test_reader)
            precision_total = 0
            test_total = 0
            recall_total = 0
            truth_total = 0
            for truth_row in truth_list:
                truth_row = list(map(lambda i: i.strip("\""), truth_row))
                for test_row in test_list:
                    test_row = list(map(lambda i: i.strip("\""), test_row))
                    if truth_row[0] == test_row[0]:
                        recall_count = 0
                        precision_count = 0
                        truth_tasks = list(filter(None, truth_row[1].split(",")))
                        test_tasks = list(filter(None, test_row[1].split(",")))
                        for truth_task in truth_tasks:
                            found = False
                            for test_task in test_tasks:
                                pr = fuzz.partial_ratio(truth_task.lower(), test_task.lower())
                                # Uncomment these lines to get data for choosing 70% threshold
                                # print(truth_row[0])
                                # print(truth_task.lower() + " | " + test_task.lower())
                                # print(pr)
                                if pr >= 70:
                                    found = True
                                    # print(truth_row[0])
                                    # print(truth_task.lower() + " | " + test_task.lower())
                                    # print(pr)
                                    precision_count += 1
                            if found:
                                recall_count += 1
                        # print(truth_row[0])
                        # print(precision_count, len(test_tasks))  # precision
                        # print(recall_count, len(truth_tasks))  # recall
                        precision_total += precision_count
                        test_total += len(test_tasks)
                        recall_total += recall_count
                        truth_total += len(truth_tasks)
                        break
            try:
                print("Precision:", precision_total, "/", test_total, "=", precision_total/test_total)
                print("Recall:", recall_total, "/", truth_total, "=", recall_total/truth_total)
            except ZeroDivisionError:
                print("No extracted tasks")


def evaluate_links(truth, test):
    with open(truth, "r", newline="") as truth_set:
        truth_reader = csv.reader(truth_set)
        next(truth_reader, None)
        truth_list = list(truth_reader)
        with open(test, "r", newline="") as test_set:
            test_reader = csv.reader(test_set)
            # next(test_reader, None)
            test_list = list(test_reader)
            precision_total = 0
            recall_total = 0
            for truth_row in truth_list:
                truth_row = list(map(lambda i: i.strip("\""), truth_row))
                for test_row in test_list:
                    test_row = list(map(lambda i: i.strip("\""), test_row))
                    if truth_row[0] == test_row[0]:
                        # When creating the ground truth, the tabs when copy pasting from website may be multiple spaces
                        # This matters when fuzzy matching so we remove those spaces
                        pr = fuzz.partial_ratio(re.sub(re.compile(r" +"), " ", truth_row[1].lower()), test_row[1].lower())
                        # print(truth_row[0])
                        # print(truth_row[1].lower())
                        # print(test_row[1].lower())
                        # print(pr)
                        if pr >= 95:
                            recall_total += 1
                            precision_total += 1
            try:
                print("Precision:", precision_total, "/", len(test_list), "=", precision_total/len(test_list))
                print("Recall", recall_total, "/", len(truth_list), "=", recall_total / len(truth_list))
            except ZeroDivisionError:
                print("No code example links")


if __name__ == '__main__':
    for file in os.listdir("truth"):
        truth_file = os.path.join("truth", file)
        for file2 in os.listdir("results"):
            test_file = os.path.join("results", file2)
            if file == file2:
                print(file, file2)
                if re.search(re.compile(r"(?<=_).+(?=\.)"), file)[0] == "tasks":
                    evaluate_tasks(truth_file, test_file)
                else:
                    evaluate_links(truth_file, test_file)
                print()
                break