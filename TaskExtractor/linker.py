import errno
import functools
import os
import subprocess
import re
import csv
import html

from fuzzywuzzy import fuzz
from pyquery import PyQuery as pq
from urllib.request import Request, urlopen

LINKS_FILE = os.path.normpath("results/links.csv")
TASKS_FILE = os.path.normpath("results/tasks.csv")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def call_extractor(inp):
    inp = inp.replace("’", "'")
    result = subprocess.run(["java", "-jar", "StringToTasks.jar", inp.encode("utf-8").decode("utf-8")],
                            stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


def get_paragraphs_and_tasks(paragraphs, task_file):
    with open(task_file, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        for paragraph in paragraphs.items():
            if len(paragraph[0].classes) == 0:
                extracted = call_extractor(paragraph.text())
                if extracted:
                    extracted = extracted.replace("\r\n", ",")
                    extracted = extracted.replace("\n", ",")
                    writer.writerow([paragraph.text().strip(), extracted])


def fuzzy_compare(potential, paragraph):
    return fuzz.partial_ratio(potential, paragraph)


def link_code_examples_and_paragraphs(code_examples, paragraphs, link_file):
    if os.path.isfile(link_file):
        mode = "a"
    else:
        mode = "w"
    with open(link_file, mode, encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        for example in code_examples.items():
            if example.parent()[0].tag != "p":
                code = example
                # Look for the closest parent with siblings
                while example.siblings().length == 0:
                    example = example.parent()

                # Find the paragraph that is right above the code example not crossing a header
                paragraph = None
                for child in example.parent().children():
                    # If the current child is a header then any potential paragraph previously should not be relevant
                    if re.match(re.compile("h[0-6]"), child.tag):
                        paragraph = None
                    elif child.text and child.text.count(" ") > 2:
                        for i, ratio in enumerate(
                                list(map(functools.partial(fuzzy_compare, child.text.strip()), paragraphs))):
                            if ratio >= 95:
                                paragraph = paragraphs[i]
                    # If we reach the code example then break, since according to our heuristic,
                    # explanations are not below examples
                    if example[0] == child:
                        break
                if paragraph is not None:
                    writer.writerow([paragraph, code.text()])


def filename_maker(url, ftype):
    filename = (url.split("/")[-1] if url.split("/")[-1] != "" else url.split("/")[-2])
    if "." in filename:
        filename = filename.split(".")[-2] + "_" + ftype + ".csv"
    else:
        filename = filename + "_" + ftype + ".csv"
    return os.path.normpath("results/" + filename)


def extract_and_link(url):
    p_file = extract_tasks(url)

    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    raw_html = pq(content)
    code_examples = raw_html("code")
    pre_examples = raw_html("pre")
    if os.path.basename(os.getcwd()) != "TaskExtractor":
        os.chdir("TaskExtractor")
    with open(p_file, "r", newline="") as p:
        paragraphs = list(e[0] for e in list(csv.reader(p)))
        link_file = filename_maker(url, "links")
        # Taken from: https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
        # User Matt, at 10:56 am MDT
        try:
            os.remove(link_file)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
        link_code_examples_and_paragraphs(code_examples, paragraphs, link_file)
        link_code_examples_and_paragraphs(pre_examples, paragraphs, link_file)
    os.chdir("..")


# Extracts the paragraphs from the HTML and uses TaskExtractor to extract the tasks
# Then returns the paragraphs that had extracted tasks
def extract_tasks(url):
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    raw_html = pq(content)
    if os.path.basename(os.getcwd()) != "TaskExtractor":
        os.chdir("TaskExtractor")
    filename = filename_maker(url, "tasks")
    get_paragraphs_and_tasks(raw_html("p"), filename)
    os.chdir("..")
    return filename


def extract_paragraphs(url, out_file):
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    raw_html = pq(content)
    paragraphs = raw_html("p")
    with open(out_file, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_MINIMAL)
        for paragraph in paragraphs.items():
            if len(paragraph[0].classes) == 0:
                writer.writerow([paragraph.text().strip()])
