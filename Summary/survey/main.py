import csv
import os.path
from pprint import pprint
import pandas as pd
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


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


def filter_responses():
    with open("responses.csv", "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        column_names = next(reader, None)
        filtered_responses = []
        for response in reader:
            add = False
            for i in range(5, len(column_names)):
                if response[i] != "NULL" and response[i] != "":
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
    return column_names, filtered_responses


def sort_responses(columns, responses):
    overall_responses = dict()
    familiar_responses = dict()
    unfamiliar_responses = dict()
    for response in responses:
        for idx, value in enumerate(response):
            if response[4] == "1":
                if columns[idx] in familiar_responses:
                    familiar_responses[columns[idx]].append(value)
                else:
                    familiar_responses[columns[idx]] = [value]
            else:
                if columns[idx] in unfamiliar_responses:
                    unfamiliar_responses[columns[idx]].append(value)
                else:
                    unfamiliar_responses[columns[idx]] = [value]
            if columns[idx] in overall_responses:
                overall_responses[columns[idx]].append(value)
            else:
                overall_responses[columns[idx]] = [value]
    return overall_responses, familiar_responses, unfamiliar_responses


def create_violin(dataframe, filename):
    df = dataframe.copy()
    df.dropna(subset=["general_rating"], inplace=True)
    general_rating = df.general_rating
    df = dataframe.copy()
    df.dropna(subset=["task_list"], inplace=True)
    task_list = df.task_list
    df = dataframe.copy()
    df.dropna(subset=["code_examples_methods"], inplace=True)
    code_examples_methods = df.code_examples_methods
    df = dataframe.copy()
    df.dropna(subset=["code_examples_classes"], inplace=True)
    code_examples_classes = df.code_examples_classes
    df = dataframe.copy()
    df.dropna(subset=["text_readability"], inplace=True)
    text_readability = df.text_readability
    df = dataframe.copy()
    df.dropna(subset=["code_readability"], inplace=True)
    code_readability = df.code_readability
    df = dataframe.copy()
    df.dropna(subset=["consistency"], inplace=True)
    consistency = df.consistency
    df = dataframe.copy()
    df.dropna(subset=["navigability"], inplace=True)
    navigability = df.navigability

    # Extract Figure and Axes instance
    fig, ax = plt.subplots(figsize=(13, 11))

    # Create a plot
    # values = [general_rating, task_list, code_examples_methods, code_examples_classes, text_readability, code_readability, consistency, navigability, usefulness]
    values = [navigability, consistency, code_readability,
              text_readability, code_examples_classes, code_examples_methods,
              task_list, general_rating]
    labels = ["Navigability", "Documentation/\nSource code similarity", "Code Readability",
              "Text Readability", "Class Examples", "Method Examples",
              "Task List", "General Rating"]
    ax.violinplot(values, showmedians=True, vert=False)
    ax.set_yticks([1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xticks([1, 2, 3, 4, 5])
    # Add title
    ax.set_title('Distribution of Ratings per Question', fontsize=16)
    ax.set_xlabel("Rating", fontsize=14)
    ax.set_ylabel("Metrics", fontsize=14)
    # plt.show()
    plt.savefig(filename)
    plt.close()


def main():
    # columns, responses = filter_responses()
    # overall, familiar, unfamiliar = sort_responses(columns, responses)
    # overall_dist, overall_rows = calculate_distribution(overall)
    # familiar_dist, familiar_rows = calculate_distribution(familiar)
    # unfamiliar_dist, unfamiliar_rows = calculate_distribution(unfamiliar)
    # with open("results/distributions.csv", "w", encoding="utf-8",
    #           newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(
    #         ["Rating", "General rating", "Task list", "Code example methods",
    #          "Code example classes", "Text readability", "Code readability",
    #          "Consistency", "Navigability", "Usefulness", "Matching"])
    #     writer.writerows(overall_rows)
    #     writer.writerow([])
    #     writer.writerows(familiar_rows)
    #     writer.writerow([])
    #     writer.writerows(unfamiliar_rows)

    if not os.path.isdir("plots"):
        os.mkdir("plots")
    dataframe = pd.read_csv("responses_filtered.csv", on_bad_lines="warn", encoding="ISO-8859-1")
    create_violin(dataframe, "plots/overall_distributions.png")
    create_violin(dataframe.loc[dataframe["familiar"] == 1], "plots/familiar_distributions.png")
    create_violin(dataframe.loc[dataframe["familiar"] == 0], "plots/unfamiliar_distributions.png")

    df = dataframe.copy()
    df.dropna(subset=["usefulness"], inplace=True)
    usefulness = df.usefulness
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.violinplot(usefulness, showmedians=True)
    # ax.set_title('Distribution of Usefulness Ratings', fontsize=16)
    ax.set_yticks([1, 2, 3, 4, 5])
    plt.tick_params(axis="x", which="both", bottom=False, top=False,
                    labelbottom=False)
    ax.set_ylabel("Rating", fontsize=14)
    plt.savefig("plots/usefulness_distribution.png")
    plt.close()

    df = dataframe.copy()
    df.dropna(subset=["matching"], inplace=True)
    matching = df.matching
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.violinplot(matching, showmedians=True)
    # ax.set_title('Distribution of Matching Ratings', fontsize=16)
    ax.set_yticks([1,2,3,4,5])
    plt.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)
    ax.set_ylabel("Rating", fontsize=14)
    plt.savefig("plots/matching_distribution.png")
    plt.close()

    df = dataframe.copy()
    df.dropna(subset=["years_experience"], inplace=True)
    years_experience_filtered = df.years_experience
    dataframe = pd.read_csv("responses.csv", on_bad_lines="warn", encoding="ISO-8859-1")
    dataframe.dropna(subset=["years_experience"], inplace=True)
    years_experience_unfiltered = dataframe[dataframe["years_experience"] < 41].years_experience
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(10, 10))
    ax1.violinplot(years_experience_unfiltered, showmedians=True, showextrema=True)
    ax1.set_title('Distribution of Years Experience (168)', fontsize=16)
    ax1.set_ylabel("Years Experience", fontsize=14)
    ax2.violinplot(years_experience_filtered, showmedians=True, showextrema=True)
    ax2.set_title('Distribution of Years Experience (25)', fontsize=16)
    ax2.set_ylabel("Years Experience", fontsize=14)
    # ax.set_yticks([1, 2, 3, 4, 5])
    ax1.set_xticks([])
    ax1.axis(ymin=0, ymax=45)
    ax2.set_xticks([])
    ax2.axis(ymin=0, ymax=45)
    # plt.tick_params(axis="x", which="both", bottom=False, top=False,
    #                 labelbottom=False)
    fig.tight_layout(pad=1.5)
    plt.savefig("plots/years_experience_distribution.png")
    plt.close()

    # WRITE AVERAGES
    # with open("results/overall_averages.txt", "w", encoding="utf-8") as f:
    #     pprint(calculate_average(overall), f)
    # with open("results/familiar_averages.txt", "w", encoding="utf-8") as f:
    #     pprint(calculate_average(familiar), f)
    # with open("results/unfamiliar_averages.txt", "w", encoding="utf-8") as f:
    #     pprint(calculate_average(unfamiliar), f)
    # with open("results/responses.csv", "w", encoding="utf-8", newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["Type", "Years experience", "Familiar", "General rating",
    #                      "Task list", "Code example methods", "Code example classes",
    #                      "Text readability", "Code readability", "Consistency",
    #                      "Navigability", "Usefulness", "Matching"])
    #     lis = ["overall"]
    #     lis.extend(dict_to_list(calculate_average(overall)))
    #     writer.writerow(lis)
    #     lis = ["familiar"]
    #     lis.extend(dict_to_list(calculate_average(familiar)))
    #     writer.writerow(lis)
    #     lis = ["unfamiliar"]
    #     lis.extend(dict_to_list(calculate_average(unfamiliar)))
    #     writer.writerow(lis)

    print("Done")


if __name__ == '__main__':
    main()
