import csv
import os
import re
from fuzzywuzzy import fuzz


def evaluate_tasks(truth, test, filename):
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
            seen = set()
            with open(os.path.normpath(os.path.join("comparison", filename)), "w", encoding="utf-8", newline="") as out_file:
                task_writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
                task_writer.writerow(["Paragraph", "Ground truth tasks", "Program tasks", "Partial Ratio"])
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    for test_row in test_list:
                        test_row = list(map(lambda i: i.strip("\""), test_row))
                        if truth_row[0] == test_row[0]:
                            recall_count = 0
                            precision_count = 0
                            truth_tasks = list(filter(None, truth_row[1].split("\n")))
                            test_tasks = list(filter(None, test_row[1].split(",")))
                            for truth_task in truth_tasks:
                                found = False
                                for test_task in test_tasks:
                                    pr = fuzz.partial_ratio(truth_task.lower(), test_task.lower())
                                    seen.add(truth_row[0])
                                    task_writer.writerow([truth_row[0], truth_task.lower(), test_task.lower(), pr])
                                    if pr >= 70:
                                        found = True
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
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    if truth_row[0] not in seen:
                        truth_tasks = list(filter(None, truth_row[1].split("\n")))
                        for truth_task in truth_tasks:
                            task_writer.writerow([truth_row[0], truth_task.lower()])
                for test_row in test_list:
                    test_row = list(map(lambda i: i.strip("\""), test_row))
                    if test_row[0] not in seen:
                        test_tasks = list(filter(None, test_row[1].split("\n")))
                        for test_task in test_tasks:
                            task_writer.writerow([test_row[0], "", test_task.lower()])
                try:
                    # print("Precision:", precision_total, "/", test_total, "=", precision_total/test_total)
                    # print("Recall:", recall_total, "/", truth_total, "=", recall_total/truth_total)
                    return [precision_total, test_total, precision_total/test_total, recall_total, truth_total, recall_total/truth_total]
                except ZeroDivisionError:
                    # print("No extracted tasks")
                    return ["N/A"] * 6


def evaluate_links(truth, test, filename):
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
            seen = set()
            with open(os.path.normpath(os.path.join("comparison", filename)), "w", encoding="utf-8", newline="") as out_file:
                link_writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
                link_writer.writerow(["Paragraph", "Ground Truth link", "Program link", "Partial ratio"])
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    for test_row in test_list:
                        test_row = list(map(lambda i: i.strip("\""), test_row))
                        if truth_row[0] == test_row[0]:
                            seen.add(truth_row[0])
                            # When creating the ground truth, the tabs when copy pasting from website may be multiple spaces
                            # This matters when fuzzy matching so we remove those spaces
                            pr = fuzz.partial_ratio(re.sub(re.compile(r" +"), " ", truth_row[1].lower()), test_row[1].lower())
                            link_writer.writerow([truth_row[0], truth_row[1].lower(), test_row[1].lower(), pr])
                            if pr >= 95:
                                recall_total += 1
                                precision_total += 1
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    if truth_row[0] not in seen:
                        link_writer.writerow([truth_row[0], truth_row[1].lower()])
                for test_row in test_list:
                    test_row = list(map(lambda i: i.strip("\""), test_row))
                    if test_row[0] not in seen:
                        link_writer.writerow([test_row[0], "", test_row[1].lower()])
                try:
                    # print("Precision:", precision_total, "/", len(test_list), "=", precision_total/len(test_list))
                    # print("Recall", recall_total, "/", len(truth_list), "=", recall_total / len(truth_list))
                    return [precision_total, len(test_list), precision_total/len(test_list), recall_total, len(truth_list), recall_total/len(truth_list)]
                except ZeroDivisionError:
                    # print("No code example links")
                    return ["N/A"] * 6


if __name__ == '__main__':
    with open(os.path.normpath("comparison/totals.csv"), "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["File", "Correct extracted tasks", "Total extracted tasks", "Precision", "Correct truth tasks", "Total truth tasks", "Recall"])
        for file in os.listdir("truth"):
            truth_file = os.path.join("truth", file)
            for file2 in os.listdir("results"):
                test_file = os.path.join("results", file2)
                if file == file2:
                    row = [file]
                    if re.search(re.compile(r"(?<=_).+(?=\.)"), file)[0] == "tasks":
                        row = [*row, *evaluate_tasks(truth_file, test_file, file)]
                    else:
                        row = [*row, *evaluate_links(truth_file, test_file, file)]
                    writer.writerow(row)
                    break
