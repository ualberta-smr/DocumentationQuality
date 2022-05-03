import html
import re
import csv
import subprocess
import os

import util
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from TaskExtractor.filters.json_filter import json_filter


# Extracts paragraphs from the HTML and uses TaskExtractor to extract the tasks
# Then returns the paragraphs that had extracted tasks
def extract_tasks(library_name, page, domain):
    req = Request(url=page, headers=util.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    filename = util.make_filename_from_url(library_name, page, "tasks")
    domain_filter = _get_domain_filter(domain)
    get_paragraphs_and_tasks(soup.find_all("p"), filename, domain_filter)


def _get_domain_filter(domain):
    domain_filter = None
    if domain == "json":
        domain_filter = json_filter
    # elif domain == "nlp":
    #     pass
    #     filter = nlp_filter
    # elif domain == "jquery":
    #     filter = jquery_filter
    # elif domain == "react":
    #     filter = react_filter
    return domain_filter


# Unused but provided to write to file all paragraphs extracted from page
def extract_paragraphs(page, out_file):
    req = Request(url=page, headers=util.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    with open(out_file, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        for paragraph in paragraphs:
            if len(paragraph[0].classes) == 0:
                writer.writerow([paragraph.text().strip()])


def get_paragraphs_and_tasks(paragraphs, task_file, domain_filter):
    tt = re.compile(r"</?tt>")
    with open(task_file, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        writer.writerow(["Paragraph", "Tasks"])
        for paragraph in paragraphs:
            if not paragraph.has_attr("class"):
                text = preprocess(paragraph.prettify())
                extracted = call_extractor(text)
                if extracted:
                    extracted = extracted.replace("\r\n", "\n")
                    extracted = re.sub(tt, "", extracted)
                    extracted = domain_filter(extracted)
                    if extracted:
                        writer.writerow(
                            [paragraph.get_text().strip(), extracted])
    if os.stat(task_file).st_size == 0:
        os.remove(task_file)


def preprocess(text):
    code = re.compile(r"(?:<code|<pre).*?>(.*?)</(?:code|pre)>")
    code_terms = re.findall(code, text)
    for code_term in code_terms:
        text = re.sub(code, "<tt>" + code_term + "</tt>", text, 1)
    # We want to replace all tags except <tt> and <h1-6>
    replaceable = re.compile(r"<(?!/?t{2})(?!h[1-6]).*?>")
    text = re.sub(replaceable, "", text)
    return text


def call_extractor(inp):
    # This ensures the input is in UTF-8 encoding
    inp = inp.encode("utf-8").decode("utf-8")
    # However, since this uses the running OS to run the jar, the result
    # from stdout may not be utf-8, in fact it's probably ISO-8859-1
    result = subprocess.run(["java",
                             "-jar",
                             "StringToTasks.jar",
                             inp],
                            stdout=subprocess.PIPE)
    # NOTE: As soon as every machine starts using UTF-8 inherently, we can
    # change this decoding to be "utf-8" instead of "ISO-8859-1" which is
    # assumed to be the most widely used encoding on Windows and Unix systems.
    # https://en.wikipedia.org/wiki/ISO/IEC_8859-1
    return result.stdout.decode("ISO-8859-1")
