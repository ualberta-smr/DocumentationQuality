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

        print(calculate_average(overall_averages))
        print(calculate_average(familiar_averages))
        print(calculate_average(unfamiliar_averages))
        print("Done")


if __name__ == '__main__':
    main()
