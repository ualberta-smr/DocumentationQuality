import csv
import os.path
from pprint import pprint
import csv


def calculate_average(response_dict):
    averages = dict()
    non_average_columns = ["id", "session_key", "library_name", "where_see",
                           "general_feedback"]
    for key, value in response_dict.items():
        if key not in non_average_columns:
            values = [int(item) for item in
                      list(filter(lambda item: item != "NULL", value))]
            if key == "familiar":
                averages[key] = str(sum(values)) + "/" + str(len(values))
            else:
                if values:
                    averages[key] = sum(values) / len(values)
                else:
                    averages[key] = None
    return averages


def dict_to_list(dic):
    values = []
    for value in dic.values():
        values.append(value)
    return values


def calculate_distribution(response_dict):
    distribution = dict()
    non_dist_columns = ["id", "session_key", "library_name", "where_see",
                        "general_feedback"]
    for key, raw_values in response_dict.items():
        if key not in non_dist_columns:
            values = [int(item) for item in
                      list(filter(lambda item: item != "NULL", raw_values))]
            for val in values:
                if key not in distribution:
                    if key != "years_experience" and key != "familiar":
                        distribution[key] = dict({1: 0,
                                                  2: 0,
                                                  3: 0,
                                                  4: 0,
                                                  5: 0})
                    else:
                        distribution[key] = dict()
                if val not in distribution[key]:
                    distribution[key][val] = 1
                else:
                    distribution[key][val] += 1

    for key, values in distribution.items():
        if key != "years_experience" and key != "familiar":
            row = [0, 0, 0, 0, 0]
            for value, count in values.items():
                row[value - 1] = count
            distribution[key] = row
    mapping = {"general_rating": 1,
               "task_list": 2,
               "code_examples_methods": 3,
               "code_examples_classes": 4,
               "text_readability": 5,
               "code_readability": 6,
               "consistency": 7,
               "navigability": 8,
               "usefulness": 9,
               "matching": 10}
    rows = [[1, None, None, None, None, None, None, None, None, None, None],
            [2, None, None, None, None, None, None, None, None, None, None],
            [3, None, None, None, None, None, None, None, None, None, None],
            [4, None, None, None, None, None, None, None, None, None, None],
            [5, None, None, None, None, None, None, None, None, None, None]]
    for key, values in distribution.items():
        if key != "years_experience" and key != "familiar":
            index = mapping[key]
            for i in range(len(values)):
                rows[i][index] = values[i]
    return distribution, rows


def main():
    with open("responses.csv", "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        column_names = next(reader, None)
        filtered_responses = []
        for response in reader:
            add = False
            for i in range(5, len(column_names)):
                if response[i] != "NULL":
                    add = True
                    break
            if add:
                filtered_responses.append(response)
    if not os.path.isdir("results"):
        os.mkdir("results")
    with open("results/filtered_responses.csv", "w", encoding="utf-8",
              newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["ID", "Session key", "Library name", "Years experience",
             "Familiar", "General rating",
             "Task list", "Code example methods", "Code example classes",
             "Text readability", "Code readability", "Consistency",
             "Navigability", "Usefulness", "Where see", "Matching",
             "General Feedback"])
        writer.writerows(filtered_responses)

    overall_averages = dict()
    familiar_averages = dict()
    unfamiliar_averages = dict()
    for response in filtered_responses:
        for idx, value in enumerate(response):
            if response[4] == "1":
                if column_names[idx] in familiar_averages:
                    familiar_averages[column_names[idx]].append(value)
                else:
                    familiar_averages[column_names[idx]] = [value]
            else:
                if column_names[idx] in unfamiliar_averages:
                    unfamiliar_averages[column_names[idx]].append(value)
                else:
                    unfamiliar_averages[column_names[idx]] = [value]
            if column_names[idx] in overall_averages:
                overall_averages[column_names[idx]].append(value)
            else:
                overall_averages[column_names[idx]] = [value]

    overall_dist, overall_rows = calculate_distribution(overall_averages)
    familiar_dist, familiar_rows = calculate_distribution(familiar_averages)
    unfamiliar_dist, unfamiliar_rows = calculate_distribution(unfamiliar_averages)
    with open("results/distributions.csv", "w", encoding="utf-8",
              newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Rating", "General rating", "Task list", "Code example methods",
             "Code example classes", "Text readability", "Code readability",
             "Consistency", "Navigability", "Usefulness", "Matching"])
        writer.writerows(overall_rows)
        writer.writerow([])
        writer.writerows(familiar_rows)
        writer.writerow([])
        writer.writerows(unfamiliar_rows)


    with open("results/overall_averages.txt", "w", encoding="utf-8") as f:
        pprint(calculate_average(overall_averages), f)
    with open("results/familiar_averages.txt", "w", encoding="utf-8") as f:
        pprint(calculate_average(familiar_averages), f)
    with open("results/unfamiliar_averages.txt", "w", encoding="utf-8") as f:
        pprint(calculate_average(unfamiliar_averages), f)
    with open("results/responses.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Years experience", "Familiar", "General rating",
                         "Task list", "Code example methods", "Code example classes",
                         "Text readability", "Code readability", "Consistency",
                         "Navigability", "Usefulness", "Matching"])
        lis = ["overall"]
        lis.extend(dict_to_list(calculate_average(overall_averages)))
        writer.writerow(lis)
        lis = ["familiar"]
        lis.extend(dict_to_list(calculate_average(familiar_averages)))
        writer.writerow(lis)
        lis = ["unfamiliar"]
        lis.extend(dict_to_list(calculate_average(unfamiliar_averages)))
        writer.writerow(lis)

    print("Done")


if __name__ == '__main__':
    main()
