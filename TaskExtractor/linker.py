import functools
import os
import subprocess
from fuzzywuzzy import fuzz
import re
from pyquery import PyQuery as pq


LINKS_FILE = os.path.normpath("results/links.txt")
TASKS_FILE = os.path.normpath("results/tasks.txt")


def call_extractor(inp):
    inp = inp.replace("’", "'")
    result = subprocess.run(["java", "-jar", "StringToTasks.jar", inp.encode("utf-8").decode("utf-8")], stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


def get_paragraphs_and_tasks(paragraphs):
    paragraphs_w_tasks = []
    with open(TASKS_FILE, "w", encoding="utf-8") as task_file:
        os.chdir("TaskExtractor")
        for paragraph in paragraphs.items():
            if len(paragraph[0].classes) == 0:
                extract = call_extractor(paragraph.text())
                if extract:
                    paragraphs_w_tasks.append(paragraph.text().strip())
                    task_file.write(paragraph.text().strip())
                    task_file.write("\n")
                    task_file.write(extract.replace("\r\n", "\n"))
                    task_file.write("\n")
        os.chdir("..")
    return paragraphs_w_tasks


def fuzzy_compare(potential, paragraph):
    return fuzz.partial_ratio(potential, paragraph)


def link_code_examples_and_paragraphs(code_examples, paragraphs):
    with open(LINKS_FILE, "w", encoding="utf-8") as links_file:
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
                        for i, ratio in enumerate(list(map(functools.partial(fuzzy_compare, child.text.strip()), paragraphs))):
                            if ratio == 100:
                                paragraph = paragraphs[i]
                    # If we reach the code example then break, since according to our heuristic,
                    # explanations are not below examples
                    if example[0] == child:
                        break
                if paragraph is not None:
                    links_file.write(paragraph + "\n")
                    links_file.write(code.text() + "\n\n")


def link():
    raw_html = pq(url="https://stanfordnlp.github.io/CoreNLP/ner.html")
    paragraphs = get_paragraphs_and_tasks(raw_html("p"))

    code_examples = raw_html("code")

    link_code_examples_and_paragraphs(code_examples, paragraphs)
