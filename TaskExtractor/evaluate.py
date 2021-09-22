import csv
from fuzzywuzzy import fuzz


def find_longer(list_one, list_two):
    return (list_one, list_two) if len(list_one) > len(list_two) else (list_two, list_one)


def evaluate(truth, test):
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
            for truth_row in truth_list:
                truth_row = list(map(lambda i: i.strip("\""), truth_row))
                for test_row in test_list:
                    if truth_row[0] == test_row[0]:
                        count = 0
                        truth_tasks = list(filter(None, truth_row[1].split(",")))
                        test_tasks = list(filter(None, test_row[1].split(",")))
                        for truth_task in truth_tasks:
                            for test_task in test_tasks:
                                pr = fuzz.partial_ratio(truth_task.lower(), test_task.lower())
                                # Uncomment these lines to get data for choosing 70% threshold
                                # print(truth_row[0])
                                # print(truth_task.lower() + " | " + test_task.lower())
                                # print(pr)
                                if pr > 69:
                                    print(truth_row[0])
                                    print(truth_task.lower() + " | " + test_task.lower())
                                    print(pr)
                                    count += 1
                        print(truth_row[0])
                        print(count, len(test_tasks), len(truth_tasks))


if __name__ == '__main__':
    evaluate("results/TaskExtractionGT - stanford NER.csv", "results/ner_tasks.csv")
