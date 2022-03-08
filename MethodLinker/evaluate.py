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
            with open(
                    os.path.normpath("comparison/" + truth_file.split("\\")[1]),
                    "w", encoding="utf-8", newline="") as results:
                result_writer = csv.writer(results, quoting=csv.QUOTE_MINIMAL)
                result_writer.writerow(
                    ["Example", "Linked function", "Truth function", "Source",
                     "Correct"])
                truth_headers = ["example", "page", "source", "class",
                                 "function"]
                test_headers = ["example", "extracted", "linked", "source",
                                "matched"]
                for row1 in truth_list:
                    truth_row = dict(zip(truth_headers, row1))
                    for row2 in test_list:
                        test_row = dict(zip(test_headers, row2))
                        if truth_row["example"] == test_row["example"]:
                            if truth_row["function"] == test_row["linked"] \
                                and truth_row["source"] == test_row["source"] \
                                    and test_row["matched"] == "True":
                                result_writer.writerow(
                                    [truth_row["example"], test_row["linked"],
                                     truth_row["function"], truth_row["source"],
                                     1])
                                correct += 1
                            else:
                                result_writer.writerow(
                                    [truth_row["example"], test_row["linked"],
                                     truth_row["function"], truth_row["source"],
                                     0])
    return [correct, len(test_list), correct / len(test_list),  # Precision
            correct, len(truth_list), correct / len(truth_list)]  # Recall


if __name__ == '__main__':
    with open(os.path.normpath("comparison/evaluation.csv"), "w",
              encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["Repo", "Correct", "Total test", "Precision", "Correct",
             "Total truth", "Recall"])
        for file1 in os.listdir("truth"):
            truth_file = os.path.join("truth", file1)
            for file2 in os.listdir("results"):
                test_file = os.path.join("results", file2)
                if file1 == file2:
                    writer.writerow([file1.split(".")[0],
                                     *evaluate_links(truth_file, test_file)])
                    break
