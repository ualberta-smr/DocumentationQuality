import datetime
import html
import os
import re
import threading
from pathlib import Path

import gdown
import nltk
import time
import mysql.connector

from django.apps import AppConfig
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from thefuzz import fuzz

from .util import HEADERS, MYSQL_CONFIG, add_or_update_library_record, \
    add_tasks_to_db, ROOT_DIR, clone_repo, remove_old_tasks
from .TaskExtractor.main import task_extract_and_link
from .MethodLinker.main import api_methods_examples
from .Readability.main import get_readability


def get_description(library_name, doc_url):
    req = Request(url=doc_url, headers=HEADERS)
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
                                      " ".join(bigram)) == 100 and len(pot_desc) > len(description):
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
        add_or_update_library_record(
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
        remove_old_tasks(self.library_name)
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
        methods_ratio, classes_ratio = api_methods_examples(self.language,
                                                            self.library_name,
                                                            self.doc_url,
                                                            self.repo_path,
                                                            self.match_examples)
        if self.match_examples:
            add_or_update_library_record({"library_name": self.library_name,
                                          "gh_url": self.gh_url,
                                          "doc_url": self.doc_url,
                                          "methods_ratio": methods_ratio,
                                          "classes_ratio": classes_ratio,
                                          "last_updated": datetime.datetime.utcnow()
                                          })
        else:
            consistency_ratio = (0.5 * methods_ratio) + (0.5 * classes_ratio)
            add_or_update_library_record({"library_name": self.library_name,
                                          "gh_url": self.gh_url,
                                          "doc_url": self.doc_url,
                                          "consistency_ratio": consistency_ratio,
                                          "last_updated": datetime.datetime.utcnow()
                                          })
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished matching with " + ("Examples" if self.match_examples else "Signatures") + ": ")
            times.write(str(end - start))
            times.write("\n")


class Readability(threading.Thread):
    def __init__(self, library_name, language, doc_url):
        threading.Thread.__init__(self)
        self.library_name = library_name
        self.language = language
        self.doc_url = doc_url

    def run(self):
        start = time.time()
        text_score, text_ease, code_score, code_ease = get_readability(
            self.library_name, self.language, self.doc_url)
        add_or_update_library_record({"library_name": self.library_name,
                                      "text_readability_score": text_score,
                                      "text_readability_rating": text_ease,
                                      "code_readability_score": code_score,
                                      "code_readability_rating": code_ease,
                                      "last_updated:": datetime.datetime.utcnow()})
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished calculating readability: ")
            times.write(str(end - start))
            times.write("\n")


def analyze_library(language, library_name, doc_url, gh_url, domain):
    website_db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = website_db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM overview_library WHERE library_name ='" + library_name + "';")
    result = cursor.fetchone()
    clone = False
    if result:
        now = datetime.datetime.utcnow()
        if now - result["last_updated"] > datetime.timedelta(days=30):
            clone = True
    cursor.close()
    os.chdir(ROOT_DIR)
    extraction_jar = Path(ROOT_DIR + "/TaskExtractor/StringToTasks.jar")
    if not extraction_jar.exists():
        gdown.download(url="https://drive.google.com/file/d/19gV3aDLz5e6Gmb7nn29BlsfVX0AbHZ41/view?usp=sharing", output=str(extraction_jar), fuzzy=True)
    create = Create(library_name, language, domain, doc_url)
    extract = Extract(library_name, doc_url, domain)
    repo_path = clone_repo(gh_url, clone)
    match_signatures = APIMatching(library_name, language, doc_url, gh_url, repo_path, False)
    match_examples = APIMatching(library_name, language, doc_url, gh_url, repo_path, True)
    # readability = Readability(library_name, language, doc_url)

    with open("times.txt", "a") as times:
        times.write("Starting analysis for " + library_name)
        times.write("\n")

    create.start()
    extract.start()
    match_examples.start()
    match_signatures.start()
    # readability.start()


def debug_metrics(language, library_name, doc_url, gh_url, domain):
    os.chdir(ROOT_DIR)
    # description = get_description(library_name, doc_url)
    # if not description:
    #     description = "Could not find description"
    # add_or_update_library_record(
    #     {"library_name": library_name,
    #      "language": language,
    #      "domain": domain,
    #      "description": description,
    #      "doc_url": doc_url,
    #      "last_updated": datetime.datetime.utcnow()
    #      })
    #
    # task_extract_and_link(library_name, doc_url, domain)
    # remove_old_tasks(library_name)
    # add_tasks_to_db(library_name)
    #
    # repo_path = clone_repo(gh_url, True)
    # api_methods_examples(language, library_name, doc_url, repo_path, False)
    # api_methods_examples(language, library_name, doc_url, repo_path, True)
    text_score, text_ease, code_score, code_ease = get_readability(library_name,
                                                                   language,
                                                                   doc_url)
    print(text_score, text_ease, code_score, code_ease)


class AnalyzeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyze'
