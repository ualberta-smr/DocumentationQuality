import csv
import os
import re
from thefuzz import fuzz


def evaluate_tasks(truth, test, filename):
    with open(truth, "r", newline="", encoding="utf-8") as truth_set:
        truth_reader = csv.reader(truth_set)
        # Skip over the header
        next(truth_reader, None)
        truth_list = list(truth_reader)
        with open(test, "r", newline="", encoding="utf-8") as test_set:
            test_reader = csv.reader(test_set)
            next(test_reader, None)
            test_list = list(test_reader)
            precision_total = 0
            test_total = 0
            recall_total = 0
            truth_total = 0
            seen = set()
            with open(os.path.normpath(filename), "w", encoding="utf-8", newline="") as out_file:
                task_writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
                task_writer.writerow(
                    ["Paragraph", "Ground truth tasks", "Program tasks",
                     "Partial Ratio"])
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    for test_row in test_list:
                        test_row = list(map(lambda i: i.strip("\""), test_row))
                        if fuzz.ratio(truth_row[0], test_row[0]) >= 95:
                            recall_count = 0
                            precision_count = 0
                            # Remove any empty strings
                            truth_tasks = list(
                                filter(None, truth_row[1].split("\n")))
                            test_tasks = list(
                                filter(None, test_row[1].split("\n")))
                            seen.add(truth_row[0])
                            for truth_task in truth_tasks:
                                found = False
                                for test_task in test_tasks:
                                    pr = fuzz.partial_ratio(truth_task.lower(),
                                                            test_task.lower())
                                    task_writer.writerow(
                                        [truth_row[0], truth_task.lower(),
                                         test_task.lower(), pr])
                                    if pr >= 90:
                                        found = True
                                        precision_count += 1
                                        break
                                if found:
                                    recall_count += 1
                            # print(truth_row[0])
                            # print(precision_count, len(test_tasks))# precision
                            # print(recall_count, len(truth_tasks)) # recall
                            precision_total += precision_count
                            test_total += len(test_tasks)
                            recall_total += recall_count
                            truth_total += len(truth_tasks)
                            break
                # Can not use simple if truth_row[0] in seen. Need to use
                # fuzzy matching because of whitespace within the text.
                in_seen = False
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    for item in seen:
                        if fuzz.ratio(truth_row[0], item) >= 95:
                            in_seen = True
                            break
                    if not in_seen:
                        truth_tasks = list(
                            filter(None, truth_row[1].split("\n")))
                        for truth_task in truth_tasks:
                            truth_total += 1
                            task_writer.writerow(
                                [truth_row[0], truth_task.lower()])
                    in_seen = False
                for test_row in test_list:
                    test_row = list(map(lambda i: i.strip("\""), test_row))
                    for item in seen:
                        if fuzz.ratio(test_row[0], item) >= 95:
                            in_seen = True
                            break
                    if not in_seen:
                        test_tasks = list(filter(None, test_row[1].split("\n")))
                        for test_task in test_tasks:
                            test_total += 1
                            task_writer.writerow(
                                [test_row[0], "", test_task.lower()])
                    in_seen = False
                try:
                    # print("Precision:", precision_total, "/", test_total, "=",
                    #       precision_total / test_total)
                    # print("Recall:", recall_total, "/", truth_total, "=",
                    #       recall_total / truth_total)
                    return [precision_total, test_total,
                            round(precision_total / test_total, 2),
                            recall_total, truth_total,
                            round(recall_total / truth_total, 2)]
                except ZeroDivisionError:
                    # print("No extracted tasks")
                    return ["N/A"] * 6


def evaluate_links(truth, test, filename):
    with open(truth, "r", newline="", encoding="utf-8") as truth_set:
        truth_reader = csv.reader(truth_set)
        next(truth_reader, None)
        truth_list = list(truth_reader)
        with open(test, "r", newline="", encoding="utf-8") as test_set:
            test_reader = csv.reader(test_set)
            next(test_reader, None)
            test_list = list(test_reader)
            precision_total = 0
            recall_total = 0
            paragraphs_with_tasks = 0
            seen = set()
            with open(os.path.normpath(filename), "w", encoding="utf-8", newline="") as out_file:
                link_writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
                link_writer.writerow(
                    ["Paragraph", "Ground Truth link", "Program link", "Has Tasks",
                     "Partial ratio"])
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    for test_row in test_list:
                        test_row = list(map(lambda i: i.strip("\""), test_row))
                        if fuzz.ratio(truth_row[0], test_row[0]) >= 95:
                            seen.add(truth_row[0])
                            # When creating the ground truth, the tabs when copy
                            # pasting from website may be multiple spaces
                            # This matters when fuzzy matching so we remove
                            # those spaces
                            pr = fuzz.ratio(re.sub(re.compile(r" +"), " ",
                                                   truth_row[1].lower()),
                                            re.sub(re.compile(r" +"), " ",
                                                   test_row[1].lower()))
                            link_writer.writerow(
                                [truth_row[0], truth_row[1].lower(),
                                 test_row[1].lower(), truth_row[2] if len(truth_row) > 2 else "FALSE",  pr])
                            if len(truth_row) > 2 and truth_row[2] == "TRUE":
                                paragraphs_with_tasks += 1
                            if pr >= 95:
                                recall_total += 1
                                precision_total += 1
                in_seen = False
                for truth_row in truth_list:
                    truth_row = list(map(lambda i: i.strip("\""), truth_row))
                    for item in seen:
                        if fuzz.ratio(truth_row[0], item) >= 95:
                            in_seen = True
                            break
                    if not in_seen:
                        if len(truth_row) > 2 and truth_row[2] == "TRUE":
                            paragraphs_with_tasks += 1
                        link_writer.writerow(
                            [truth_row[0], truth_row[1].lower(), "", truth_row[2] if len(truth_row) > 2 else "FALSE"])
                    in_seen = False
                for test_row in test_list:
                    test_row = list(map(lambda i: i.strip("\""), test_row))
                    for item in seen:
                        if fuzz.ratio(test_row[0], item) >= 95:
                            in_seen = True
                    if not in_seen:
                        link_writer.writerow(
                            [test_row[0], "", test_row[1].lower(), test_row[2] if len(test_row) > 2 else "FALSE"])
                    in_seen = False
                try:
                    # print("Precision:", precision_total, "/", len(test_list),
                    #       "=", precision_total / len(test_list))
                    # print("Recall", recall_total, "/", len(truth_list), "=",
                    #       recall_total / len(truth_list))
                    row = [precision_total, len(test_list), round(precision_total / len(test_list), 2),
                            recall_total, len(truth_list), round(recall_total / len(truth_list), 2)]
                    if paragraphs_with_tasks > 0:
                        row.append(paragraphs_with_tasks)
                        row.append(round(precision_total / paragraphs_with_tasks, 2))
                        row.append(round(recall_total / paragraphs_with_tasks, 2))
                    return row
                except ZeroDivisionError:
                    # print("No code example links")
                    return ["N/A"] * 6


if __name__ == '__main__':
    # x = evaluate_tasks("truth/orjson_tasks.csv", "results/orjson/orjson_tasks.csv", "comparison/orjson_tasks.csv")
    # y = evaluate_links("truth/orjson_links.csv", "results/orjson/orjson_links.csv", "comparison/orjson_links.csv")
    # print(x, y)
    with open(os.path.normpath("comparison/totals.csv"), "w", encoding="utf-8",
              newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["File",
             "Correct extracted tasks/linked code examples", "Total extracted tasks/linked code examples", "Precision",
             "Correct truth tasks/code examples", "Total truth tasks/code examples", "Recall",
             "Total paragraphs with tasks", "Precision", "Recall"])
        for file in os.listdir("truth"):
            truth_file = os.path.join("truth", file)
            for root, dirs, files in os.walk("results"):
                if files:
                    for file2 in files:
                        test_file = os.path.join(root, file)
                        if file == file2:
                            row = [file]
                            if re.search(re.compile(r"(?<=_).+(?=\.)"), file)[0] == "tasks":
                                row = [*row, *evaluate_tasks(truth_file, test_file, os.path.normpath(os.path.join("comparison", file)))]
                            else:
                                row = [*row, *evaluate_links(truth_file, test_file, os.path.normpath(os.path.join("comparison", file)))]
                            writer.writerow(row)
                            break
