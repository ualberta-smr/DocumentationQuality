import datetime
import html
import json
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

from .HCI.main import run_checklist
from .TaskExtractor.main import task_extract_and_link
from .MethodLinker.main import api_methods_examples
from .Readability.main import get_readability
from .util import HEADERS, MYSQL_CONFIG, add_or_update_library_record, \
    add_tasks_to_db, ROOT_DIR, clone_repo, remove_old_tasks


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


class Create:
    def __init__(self, library_name, language, domain, doc_url, gh_url):
        self.library_name = library_name
        self.language = language
        self.domain = domain
        self.doc_url = doc_url
        self.gh_url = gh_url

    def run(self):
        start = time.time()
        description = get_description(self.library_name, self.doc_url)
        if not description:
            try:
                req = Request(url=self.gh_url, headers=HEADERS)
                content = html.unescape(urlopen(req).read().decode("utf-8"))
                soup = BeautifulSoup(content, "html.parser")
                for h2 in soup.find_all("h2"):
                    if h2.string == 'About':
                        description = h2.fetchNextSiblings()[0].get_text().strip()
            except Exception as e:
                description = "Could not find description"
        add_or_update_library_record(
            {"library_name": self.library_name,
             "language": self.language,
             "domain": self.domain,
             "description": description,
             "doc_url": self.doc_url,
             "gh_url": self.gh_url,
             "task_list_done": False,
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
        add_or_update_library_record(
            {"library_name": self.library_name,
             "task_list_done": True,
             "last_updated": datetime.datetime.utcnow()
             })
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
        methods_linked, methods, classes_linked, classes = api_methods_examples(
            self.language,
            self.library_name,
            self.doc_url,
            self.repo_path,
            self.match_examples)
        if self.match_examples:
            add_or_update_library_record({"library_name": self.library_name,
                                          "gh_url": self.gh_url,
                                          "doc_url": self.doc_url,
                                          "method_examples": methods_linked,
                                          "class_examples": classes_linked,
                                          "methods": methods,
                                          "classes": classes,
                                          "last_updated": datetime.datetime.utcnow()
                                          })
        else:
            add_or_update_library_record({"library_name": self.library_name,
                                          "gh_url": self.gh_url,
                                          "doc_url": self.doc_url,
                                          "signature_methods": methods_linked,
                                          "signature_classes": classes_linked,
                                          "methods": methods,
                                          "classes": classes,
                                          "last_updated": datetime.datetime.utcnow()
                                          })
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished matching with " + (
                "Examples" if self.match_examples else "Signatures") + ": ")
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
                                      "text_readability_score": round(
                                          text_score, 2),
                                      "text_readability_rating": text_ease,
                                      "code_readability_score": round(
                                          code_score,
                                          2) if code_score else code_score,
                                      "code_readability_rating": code_ease,
                                      "last_updated": datetime.datetime.utcnow()})
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished calculating readability: ")
            times.write(str(end - start))
            times.write("\n")


class Navigability(threading.Thread):
    def __init__(self, library_name, doc_url):
        threading.Thread.__init__(self)
        self.library_name = library_name
        self.doc_url = doc_url

    def run(self):
        start = time.time()
        navigation_dict = run_checklist(self.library_name, self.doc_url)
        add_or_update_library_record({"library_name": self.library_name,
                                      "navigability": json.dumps(navigation_dict),
                                      "last_updated": datetime.datetime.utcnow()})
        end = time.time()
        with open("times.txt", "a") as times:
            times.write("Finished calculating navigability: ")
            times.write(str(end - start))
            times.write("\n")


def clone_library(library_name, gh_url):
    os.chdir(ROOT_DIR)
    website_db = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = website_db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM overview_library WHERE library_name ='" + library_name + "';")
    result = cursor.fetchone()
    clone = True
    if result:
        now = datetime.datetime.utcnow()
        if now - result["last_updated"] < datetime.timedelta(days=30):
            clone = False
    cursor.close()

    repo_path = clone_repo(gh_url, True)
    return repo_path


def analyze_library(language, library_name, doc_url, gh_url, domain, repo_path):
    os.chdir(ROOT_DIR)
    with open("times.txt", "a") as times:
        times.write("Starting analysis for " + library_name)
        times.write("\n")
    create = Create(library_name, language, domain, doc_url, gh_url)
    create.run()

    extraction_jar = Path(ROOT_DIR + "/TaskExtractor/StringToTasks.jar")
    if not extraction_jar.exists():
        gdown.download(
            url="https://drive.google.com/file/d/19gV3aDLz5e6Gmb7nn29BlsfVX0AbHZ41/view?usp=sharing",
            output=str(extraction_jar), fuzzy=True)
    extract = Extract(library_name, doc_url, domain)
    extract.start()

    readability_jar = Path(ROOT_DIR + "/Readability/rsm.jar")
    if not readability_jar.exists():
        gdown.download(
            url="https://drive.google.com/file/d/1S5tl8fFoZLbln8MsP-f6-F7K-F66HPZb/view?usp=sharing",
            output=str(readability_jar), fuzzy=True)
    readability = Readability(library_name, language, doc_url)
    readability.start()

    navigability = Navigability(library_name, doc_url)
    navigability.start()

    if repo_path:
        match_signatures = APIMatching(library_name, language, doc_url, gh_url,
                                       repo_path, False)
        match_examples = APIMatching(library_name, language, doc_url, gh_url,
                                     repo_path, True)
        match_examples.start()
        match_signatures.start()


def debug_metrics(language, library_name, doc_url, gh_url, domain):
    os.chdir(ROOT_DIR)

    repo_path = clone_repo(gh_url, True)
    print("Done cloning")



    # methods_linked, methods, classes_linked, classes = api_methods_examples(language, library_name, doc_url, repo_path, False)
    # add_or_update_library_record({"library_name": library_name,
    #                               "gh_url": gh_url,
    #                               "doc_url": doc_url,
    #                               "signature_methods": methods_linked,
    #                               "signature_classes": classes_linked,
    #                               "methods": methods,
    #                               "classes": classes,
    #                               "last_updated": datetime.datetime.utcnow()
    #                               })

    # print('Signature: ' + str(methods_linked) + " methods: " + str(methods))

    methods_linked, methods, classes_linked, classes = api_methods_examples(language, library_name, doc_url, repo_path, True)
    print('Example: ' + str(methods_linked) + " methods: " + str(methods))
    # add_or_update_library_record({"library_name": library_name,
    #                               "gh_url": gh_url,
    #                               "doc_url": doc_url,
    #                               "method_examples": methods_linked,
    #                               "class_examples": classes_linked,
    #                               "methods": methods,
    #                               "classes": classes,
    #                               "last_updated": datetime.datetime.utcnow()
    #                               })
    print("Done method linking")



# def debug_metrics(language, library_name, doc_url, gh_url, domain):
#     os.chdir(ROOT_DIR)
#     # description = get_description(library_name, doc_url)
#     # if not description:
#     #     description = "Could not find description"
#     # add_or_update_library_record(
#     #     {"library_name": library_name,
#     #      "language": language,
#     #      "domain": domain,
#     #      "description": description,
#     #      "doc_url": doc_url,
#     #      "gh_url": gh_url,
#     #      "task_list_done": False,
#     #      "last_updated": datetime.datetime.utcnow()
#     #      })
#     # print("Done description")
#     #
#     # task_extract_and_link(library_name, doc_url, domain)
#     # remove_old_tasks(library_name)
#     # add_tasks_to_db(library_name)
#     # print("Done task extract")
#
#     repo_path = clone_repo(gh_url, True)
#     print("Done cloning")
#     # methods_linked, methods, classes_linked, classes = api_methods_examples(language, library_name, doc_url, repo_path, False)
#     # add_or_update_library_record({"library_name": library_name,
#     #                               "gh_url": gh_url,
#     #                               "doc_url": doc_url,
#     #                               "signature_methods": methods_linked,
#     #                               "signature_classes": classes_linked,
#     #                               "methods": methods,
#     #                               "classes": classes,
#     #                               "last_updated": datetime.datetime.utcnow()
#     #                               })
#
#     # print('Signature: ' + str(methods_linked) + " methods: " + str(methods))
#
#     methods_linked, methods, classes_linked, classes = api_methods_examples(language, library_name, doc_url, repo_path, True)
#     print('Example: ' + str(methods_linked) + " methods: " + str(methods))
#     # add_or_update_library_record({"library_name": library_name,
#     #                               "gh_url": gh_url,
#     #                               "doc_url": doc_url,
#     #                               "method_examples": methods_linked,
#     #                               "class_examples": classes_linked,
#     #                               "methods": methods,
#     #                               "classes": classes,
#     #                               "last_updated": datetime.datetime.utcnow()
#     #                               })
#     print("Done method linking")
#     # text_score, text_ease, code_score, code_ease = get_readability(library_name,
#     #                                                                language,
#     #                                                                doc_url)
#     # add_or_update_library_record({"library_name": library_name,
#     #                               "text_readability_score": round(text_score, 2),
#     #                               "text_readability_rating": text_ease,
#     #                               "code_readability_score": round(code_score, 2) if code_score else code_score,
#     #                               "code_readability_rating": code_ease,
#     #                               "last_updated": datetime.datetime.utcnow()})
#     # print("Done readability")
#     # navigation_dict = run_checklist(library_name, doc_url)
#     # add_or_update_library_record({"library_name": library_name,
#     #                               "navigability": json.dumps(navigation_dict),
#     #                               "last_updated": datetime.datetime.utcnow()})
#     # print("Done navigation")

class AnalyzeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyze'
