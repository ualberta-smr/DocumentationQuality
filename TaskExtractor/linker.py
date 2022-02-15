import errno
import functools
import os
import re
import csv
import html

import util
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


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


def link_tasks(page):
    paragraph_file = util.make_filename_from_url(page, "tasks")
    if os.path.exists(paragraph_file):
        req = Request(url=page, headers=util.HEADERS)
        content = html.unescape(urlopen(req).read().decode("utf-8"))
        soup = BeautifulSoup(content, "html.parser")
        code_examples = soup.find_all("code")
        pre_examples = soup.find_all("pre")
        with open(paragraph_file, "r", encoding="utf-8", newline="") as paragraphs:
            paragraphs = list(paragraph[0] for paragraph in list(csv.reader(paragraphs)))
            potential_links = util.make_filename_from_url(page, "links_pot")
            # Taken from: https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
            # Answer by User Matt, by Henry Tang, at 10:56 am MDT
            try:
                os.remove(potential_links)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
            link_code_examples_and_paragraphs(code_examples, paragraphs, potential_links)
            link_code_examples_and_paragraphs(pre_examples, paragraphs, potential_links)
        # Remove duplicates
        if os.stat(potential_links).st_size != 0:
            with open(potential_links, "r", encoding="utf-8", newline="") as potential, open(util.make_filename_from_url(page, "links"), "w", encoding="utf-8", newline="") as final:
                pot_reader = csv.reader(potential)
                link_writer = csv.writer(final)
                link_writer.writerow(["Paragraph", "Example"])
                seen = set()
                for line in pot_reader:
                    if line[1] not in seen:
                        seen.add(line[1])
                        link_writer.writerow(line)
        else:
            print("No potential example links found")
        os.remove(potential_links)
    else:
        print("No paragraphs for", page)
