import csv


def main():
    with open("responses.csv", "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)
        column_names = next(reader, None)
        responses = {}
        for column in column_names:
            responses[column] = 0
        for response in reader:
            pass


if __name__ == '__main__':
    main()
