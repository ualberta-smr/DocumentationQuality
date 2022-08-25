import datetime
import html
import os
import re
import threading
import nltk

import time

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from Analyze import util
from Analyze.MethodLinker.main import api_methods_examples
from Analyze.TaskExtractor.main import task_extract_and_link
from Analyze.TaskExtractor.website_process import add_tasks_to_db


def get_description(library_name, doc_url):
    req = Request(url=doc_url, headers=util.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    descriptions = []
    count = 0
    for p in soup.find_all("p"):
        if count < 5:
            text = re.sub(re.compile(r"[^\S ]"), " ", p.get_text())
            norm_text = text.lower()
            if norm_text and library_name.lower() in norm_text:
                descriptions.append(text)
                count += 1
        else:
            break
    description = ""
    if len(descriptions) > 1:
        for pot_desc in descriptions:
            nltk_tokens = nltk.RegexpTokenizer(r'\w+').tokenize(
                pot_desc.lower())
            for bigram in list(nltk.bigrams(nltk_tokens)):
                if fuzz.partial_ratio(library_name.lower() + " is",
                                      " ".join(bigram)) == 100 and len(
                        pot_desc) > len(description):
                    description = pot_desc
                    break
    else:
        try:
            description = descriptions[0]
        except IndexError:
            pass
    return description


class Create(threading.Thread):
    def __init__(self, library_name, language, domain, doc_url):
        threading.Thread.__init__(self)
        self.library_name = library_name
        self.language = language
        self.domain = domain
        self.doc_url = doc_url

    def run(self):
        start = time.time()
        description = get_description(self.library_name, self.doc_url)
        if not description:
            description = "Could not find description"
        util.add_or_update_library_record(
            {"library_name": self.library_name,
             "language": self.language,
             "domain": self.domain,
             "description": description,
             "doc_url": self.doc_url,
             "last_updated": datetime.datetime.utcnow()
             })
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished retrieving description: ")
            times.write(str(end - start))
            times.write("\n")


class Extract(threading.Thread):
    def __init__(self, library_name, doc_url, domain):
        threading.Thread.__init__(self)
        self.library_name = library_name
        self.doc_url = doc_url
        self.domain = domain

    def run(self):
        start = time.time()
        task_extract_and_link(self.library_name, self.doc_url, self.domain)
        add_tasks_to_db(self.library_name)
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished extracting tasks: ")
            times.write(str(end - start))
            times.write("\n")


class APIMatching(threading.Thread):
    def __init__(self, library_name, language, doc_url, gh_url, repo_path,
                 match_examples):
        threading.Thread.__init__(self)
        self.library_name = library_name
        self.language = language
        self.doc_url = doc_url
        self.gh_url = gh_url
        self.repo_path = repo_path
        self.match_examples = match_examples

    def run(self):
        start = time.time()
        api_methods_examples(self.language, self.library_name, self.doc_url,
                             self.gh_url, self.repo_path, self.match_examples)
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished matching with " + ("Examples" if self.match_examples else "Signatures") + ": ")
            times.write(str(end - start))
            times.write("\n")


def analyze_library(language, library_name, doc_url, gh_url, domain):
    os.chdir(util.ROOT_DIR)
    create = Create(library_name, language, domain, doc_url)
    extract = Extract(library_name, doc_url, domain)
    repo_path = util.clone_repo(gh_url)
    match_signatures = APIMatching(library_name, language, doc_url, gh_url, repo_path, False)
    match_examples = APIMatching(library_name, language, doc_url, gh_url, repo_path, True)

    with open("times.txt", "w") as times:
        times.write("Starting analysis for " + library_name)
        times.write("\n")

    create.start()
    extract.start()
    match_examples.start()
    match_signatures.start()


if __name__ == '__main__':
    analyze_library("python", "orjson",
                    "http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson",
                    "https://github.com/ijl/orjson.git", "json")
    # https://web.archive.org/web/20210417122335/https://www.nltk.org/api/nltk.parse.html
    # https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html
    analyze_library("python", "nltk",
                    "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html",
                    "https://github.com/nltk/nltk.git", "nlp")
    analyze_library("python", "requests",
                    "https://web.archive.org/web/20220505163814/https://docs.python-requests.org/en/latest/",
                    "https://github.com/psf/requests.git", "http")
    # http://web.archive.org/web/20211017224709/https://github.com/stleary/JSON-java
    analyze_library("java", "JSON-java", "https://github.com/stleary/JSON-java",
                    "https://github.com/stleary/JSON-java.git", "json")
    # https://stanfordnlp.github.io/CoreNLP/ner.html
    # https://stanfordnlp.github.io/CoreNLP/cmdline.html
    analyze_library("java", "CoreNLP", "https://stanfordnlp.github.io/CoreNLP",
                    "https://github.com/stanfordnlp/CoreNLP.git", "nlp")
    # https://reactjs.org/docs/components-and-props.html
    analyze_library("javascript", "React",
                    "https://reactjs.org/docs/getting-started.html",
                    "https://github.com/facebook/react.git", "dom manipulation")
    # https://api.jquery.com/jQuery.get
    analyze_library("javascript", "jQuery", "https://api.jquery.com/",
                    "https://github.com/jquery/jquery.git", "dom manipulation")
    analyze_library("javascript", "qunit", "https://api.qunitjs.com/",
                    "https://github.com/qunitjs/qunit.git", "testing")
    analyze_library("javascript", "jBinary",
                    "https://github.com/jDataView/jBinary/wiki",
                    "https://github.com/jDataView/jBinary.git",
                    "data structures")
