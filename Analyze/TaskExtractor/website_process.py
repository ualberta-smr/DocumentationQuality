import sys
import os
import csv
import shutil

from Analyze.util import ROOT_DIR, add_to_task_table


def find_raw_csvs(library_name):
    file_dict = dict()
    root = os.path.normpath(ROOT_DIR + "/TaskExtractor/results/" + library_name)
    for file in os.listdir(root):
        # NOTE: This can be hardcoded because we know 100% what the data is
        # Otherwise this is very bad practice. However, we know we need to
        # remove the "_tasks.csv" or "_links.csv" with 100% certainty
        name = file[:-10]
        if name not in file_dict:
            if file.endswith("_tasks.csv"):
                file_dict[name] = {
                    "task_file": os.path.normpath(root + "/" + file)}
            else:
                file_dict[name] = {
                    "link_file": os.path.normpath(root + "/" + file)}
        else:
            if file.endswith("_tasks.csv"):
                file_dict[name]["task_file"] = os.path.normpath(
                    root + "/" + file)
            else:
                file_dict[name]["link_file"] = os.path.normpath(
                    root + "/" + file)
    return file_dict


def process(library_name, datafiles):
    file_dict = {}
    for key, value in datafiles.items():
        task_list, link_list = None, None
        if "task_file" in value:
            task_file = open(value["task_file"], "r", encoding="utf-8",
                             newline="")
            task_reader = csv.reader(task_file)
            next(task_reader, None)
            task_list = list(task_reader)
            task_file.close()
        if "link_file" in value:
            link_file = open(value["link_file"], "r", encoding="utf-8",
                             newline="")
            link_reader = csv.reader(link_file)
            next(link_reader, None)
            link_list = list(link_reader)
            link_file.close()

        if task_list:
            for row in task_list:
                paragraph = row[0]
                tasks = row[1].split("\n")
                if paragraph not in file_dict:
                    file_dict[paragraph] = {"tasks": tasks}

        if link_list:
            for row in link_list:
                paragraph = row[0]
                if paragraph in file_dict:
                    file_dict[paragraph]["has_example"] = True
                    file_dict[paragraph]["example_page"] = row[-1]
    processed_file_name = os.path.normpath(
        ROOT_DIR + "/TaskExtractor/processed/" + key + ".csv")
    with open(processed_file_name, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["library_name", "paragraph", "task", "has_example",
                         "example_page"])
        for key, value in file_dict.items():
            for task in value["tasks"]:
                writer.writerow([library_name, key, task, 1 if "has_example" in value else 0, value[
                                     "example_page"] if "example_page" in value else ""])
    # shutil.copy(processed_file_name, os.path.normpath("\\".join(ROOT_DIR.split("\\")[:-1]) + "/Summary/overview/data/processed"))
    return processed_file_name


def add_tasks_to_db(library_name):
    files = find_raw_csvs(library_name)
    file_name = process(library_name, files)
    with open(file_name, "r", encoding="utf-8", newline="") as data:
        reader = csv.reader(data)
        next(reader)
        for line in list(reader):
            add_to_task_table({"library_name": line[0],
                               "paragraph": line[1],
                               "task": line[2],
                               "has_example": line[3],
                               "example_page": line[4]})


if __name__ == '__main__':
    add_tasks_to_db(sys.argv[1])
