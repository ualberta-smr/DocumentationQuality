import html
import re
import os
import mysql.connector

import util
from TaskExtractor import linker, extractor
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from MethodLinker import matcher


def get_webpages(doc_home):
    req = Request(url=doc_home, headers=util.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    domain = urlparse(doc_home).hostname
    if not domain:
        print("Invalid Link")

    pages = [doc_home]
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"]
        parse = urlparse(href)
        # hostname is None means it is not an external site
        # path not null means it is another path on the documentation
        # not fragment means it does not have a "#"
        # We do not want links with "#" because they're likely redundant
        if parse.hostname is None:
            if parse.path and not parse.fragment:
                url = re.match(re.compile(".+/"), doc_home)[0] + parse.path
                pages.append(url)
        elif parse.hostname == domain:
            pages.append(href)
    pages = list(dict.fromkeys(pages))
    return pages


def task_extract_and_link(library_name, url):
    pages = get_webpages(url)
    os.chdir("TaskExtractor")
    link_directory = os.path.normpath("results/" + library_name)
    if not os.path.exists(link_directory):
        os.mkdir(link_directory)
    # If checking single page, then comment out for loop
    for page in pages:
        try:
            extractor.extract_tasks(library_name, page)
            linker.link_tasks(library_name, page)
        except HTTPError:
            pass
    # extractor.extract_tasks(library_name, url)
    # linker.link_tasks(library_name, url)
    if not os.listdir(link_directory):
        os.rmdir(link_directory)
    os.chdir("..")


def _add_or_update_method_record(item_dict):
    website_db = mysql.connector.connect(
        host="localhost",
        user="djangouser",
        password="password",
        database="task_data"
    )
    cursor = website_db.cursor()
    column_names = []
    values = []
    for key, value in item_dict.items():
        column_names.append(key)
        values.append(str(value))
    query = "SELECT * FROM overview_library WHERE library_name = " + item_dict["library_name"] + ";"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        query = "UPDATE overview_library SET "
        for i in range(len(column_names)):
            query += column_names[i] + " = " + values[i] + ", "
        query = query[:-2] + " WHERE library_name = '" + item_dict["library_name"] + "'"
    else:
        query = "INSERT INTO overview_library ("
        for column in column_names:
            query += column + ", "
        query = query[:-2] + ") VALUES ("
        for value in values:
            query += value + ", "
        query = query[:-2] + ");"
    cursor.execute(query)
    website_db.commit()
    cursor.close()


def _get_description(repo_name, doc_url):
    req = Request(url=doc_url, headers=util.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    for p in soup.find_all(re.compile("^h[1-6]$")):
        print(p)


def api_methods_examples(language, repo_name, repo_url, doc_url):
    os.chdir("MethodLinker")
    pages = get_webpages(doc_url)
    example_count, total_methods, classes_count, total_classes = matcher.calculate_ratios(
        language, repo_name, repo_url, doc_url, pages)
    _add_or_update_method_record(
        {"library_name": "'" + repo_name + "'",
         # "description": _get_description(repo_name, doc_url),
         "gh_url": "'" + repo_url + "'",
         "doc_url": "'" + doc_url + "'",
         "num_method_examples": example_count,
         "num_methods": total_methods,
         "num_class_examples": classes_count,
         "num_classes": total_classes})
    print("Methods found w/ examples:", example_count)
    print("Total methods:", total_methods)
    print("Classes found w/ examples:", classes_count)
    print("Total classes:", total_classes)
    if total_methods > 0:
        print(example_count / total_methods)
    if total_classes > 0:
        print(classes_count / total_classes)
    os.chdir("..")


if __name__ == '__main__':
    # Extract tasks and link code examples
    # inp = "https://stanfordnlp.github.io/CoreNLP/index.html"
    # task_extract_and_link("CoreNLP", inp)

    # # https://github.com/ijl/orjson
    # task_extract_and_link("orjson", "http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson")
    # # https://github.com/stleary/JSON-java
    # task_extract_and_link("JSON-java", "http://web.archive.org/web/20211017224709/https://github.com/stleary/JSON-java")
    # task_extract_and_link("CoreNLP", "https://stanfordnlp.github.io/CoreNLP/ner.html")
    # task_extract_and_link("CoreNLP", "https://stanfordnlp.github.io/CoreNLP/cmdline.html")
    # # https://www.nltk.org/api/nltk.parse.html
    # task_extract_and_link("NLTK", "https://web.archive.org/web/20210417122335/https://www.nltk.org/api/nltk.parse.html")
    # # https://www.nltk.org/api/nltk.tag.html
    # task_extract_and_link("NLTK", "https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html")
    # task_extract_and_link("jQuery", "https://api.jquery.com/jQuery.get")
    # task_extract_and_link("reactjs", "https://reactjs.org/docs/components-and-props.html")
    # task_extract_and_link("requests", "https://docs.python-requests.org/en/latest/")

    # api_methods_examples("python",
    #                      "orjson",
    #                      "https://github.com/ijl/orjson.git",
    #                      "https://github.com/ijl/orjson/blob/master/README.md")
    # api_methods_examples("python",
    #                      "nltk",
    #                      "https://github.com/nltk/nltk.git",
    #                      "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html")
    # api_methods_examples("python",
    #                      "requests",
    #                      "https://github.com/psf/requests.git",
    #                      "https://docs.python-requests.org/en/latest/")
    # api_methods_examples("java",
    #                      "json-java",
    #                      "https://github.com/stleary/JSON-java.git",
    #                      "https://github.com/stleary/JSON-java")
    api_methods_examples("java",
                         "stanford-nlp",
                         "https://github.com/stanfordnlp/CoreNLP.git",
                         "https://stanfordnlp.github.io/CoreNLP")
    # api_methods_examples("javascript",
    #                      "qunit",
    #                      "https://github.com/qunitjs/qunit.git",
    #                      "https://api.qunitjs.com/")
    # api_methods_examples("javascript",
    #                      "jBinary",
    #                      "https://github.com/jDataView/jBinary.git",
    #                      "https://github.com/jDataView/jBinary/wiki")
