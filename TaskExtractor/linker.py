import errno
import functools
import os
import subprocess
import re
import csv
import html

from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


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


def preprocess(raw_html):
    code = re.compile(r"(?:<code|<pre).*?>(.*?)</(?:code|pre)>")
    text = raw_html
    if re.findall(code, text):
        for code_term in re.findall(code, text):
            text = re.sub(code, "<tt>" + code_term + "</tt>", text, 1)
    # We want to replace all tags except <tt> and <h1-6>
    replaceable = re.compile(r"<(?!/?t{2})(?!h[1-6]).*?>")
    text = re.sub(replaceable, "", text)
    return text


def get_paragraphs_and_tasks(paragraphs, task_file):
    tt = re.compile(r"</?tt>")
    with open(task_file, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        for paragraph in paragraphs:
            if not paragraph.has_attr("class"):
                text = preprocess(paragraph.prettify())
                extracted = call_extractor(text)
                if extracted:
                    extracted = extracted.replace("\r\n", "\n")
                    extracted = re.sub(tt, "", extracted)
                    # Remove the trailing comma
                    writer.writerow([paragraph.get_text().strip(), extracted[:-1]])


def fuzzy_compare(potential, paragraph):
    ratio = 0
    try:
        ratio = fuzz.ratio(potential, paragraph)
    except:
        pass
    return ratio


def link_code_examples_and_paragraphs(code_examples, paragraphs, link_file):
    if os.path.isfile(link_file):
        mode = "a"
    else:
        mode = "w"
    with open(link_file, mode, encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        for example in code_examples:
            # exclude code/pre that is inline a (p)aragraph
            if example.parent.name != "p":
                code = example
                # Look for the closest parent with siblings of tag "p" or we reach a containing div
                potential = False
                within_section = True
                while within_section:
                    if len(list(example.parent.children)) > 1:
                        for child in example.parent.children:
                            if child.name == "p":
                                potential = True
                                break
                            if child.name and re.match(re.compile("h[0-6]"), child.name):
                                within_section = False
                        if potential:
                            break
                    example = example.parent

                # Find the paragraph that is right above the code example not crossing a header
                paragraph = None
                for child in example.parent.children:
                    # If the current child is a header then any potential paragraph previously should not be relevant
                    if child.name and re.match(re.compile("h[0-6]"), child.name):
                        paragraph = None
                    elif child.name == "p" and child.get_text() and child.get_text().count(" ") > 2:
                        for i, ratio in enumerate(list(map(functools.partial(fuzzy_compare, child.get_text().strip()), paragraphs))):
                            if ratio >= 95:
                                paragraph = paragraphs[i]
                    # If we reach the code example then break, since according to our heuristic,
                    # explanations are not below examples
                    if example == child:
                        break
                if paragraph is not None:
                    writer.writerow([paragraph, code.get_text().strip()])


def filename_maker(url, ftype):
    domain_regex = re.compile(r"(?:https?://)([\w.]+)/")
    domain = re.search(domain_regex, url)[1]
    filename = (url.split("/")[-1] if url.split("/")[-1] != "" else url.split("/")[-2])
    if "." in filename:
        filename = filename.split(".")[-2] + "_" + ftype + ".csv"
    else:
        filename = filename + "_" + ftype + ".csv"
    return os.path.normpath("results/" + domain + "/" + filename)


def extract_and_link(url):
    p_file = extract_tasks(url)
    # p_file = filename_maker(url, "tasks")
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    code_examples = soup.find_all("code")
    pre_examples = soup.find_all("pre")
    if os.stat(p_file).st_size != 0:
        with open(p_file, "r", encoding="utf-8", newline="") as p:
            paragraphs = list(e[0] for e in list(csv.reader(p)))
            link_pot = filename_maker(url, "links_pot")
            # Taken from: https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
            # Answer by User Matt, by Henry Tang, at 10:56 am MDT
            try:
                os.remove(link_pot)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
            link_code_examples_and_paragraphs(code_examples, paragraphs, link_pot)
            link_code_examples_and_paragraphs(pre_examples, paragraphs, link_pot)
        # Remove duplicates
        if os.stat(link_pot).st_size != 0:
            with open(link_pot, "r", encoding="utf-8", newline="") as potential, open(filename_maker(url, "links"), "w", encoding="utf-8", newline="") as final:
                seen = set()
                pot_reader = csv.reader(potential)
                link_writer = csv.writer(final)
                for line in pot_reader:
                    if line[1] not in seen:
                        seen.add(line[1])
                        link_writer.writerow(line)
        os.remove(link_pot)
    else:
        os.remove(p_file)


# Extracts the paragraphs from the HTML and uses TaskExtractor to extract the tasks
# Then returns the paragraphs that had extracted tasks
def extract_tasks(url):
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    filename = filename_maker(url, "tasks")
    get_paragraphs_and_tasks(soup.find_all("p"), filename)
    return filename


def extract_paragraphs(url, out_file):
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    paragraphs = soup.find_all("p")
    with open(out_file, "w", encoding="utf-8", newline="") as out_file:
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        for paragraph in paragraphs:
            if len(paragraph[0].classes) == 0:
                writer.writerow([paragraph.text().strip()])
