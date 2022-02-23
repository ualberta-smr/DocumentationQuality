import html
import re
import os


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
    return domain, pages


def task_extract_and_link(url):
    domain, pages = get_webpages(url)
    os.chdir("TaskExtractor")
    link_directory = os.path.normpath("results/" + domain)
    if not os.path.exists(link_directory):
        os.mkdir(link_directory)
    # If checking single page, then comment out for loop
    # for page in pages:
    #     try:
    #         extractor.extract_tasks(page)
    #         linker.link_tasks(page)
    #     except HTTPError:
    #         pass
    extractor.extract_tasks(url)
    linker.link_tasks(url)
    if not os.listdir(link_directory):
        os.rmdir(link_directory)
    os.chdir("..")


def api_methods_examples(language, repo_name, repo_url, doc_url):
    os.chdir("MethodLinker")
    _, pages = get_webpages(doc_url)
    example_count, total_methods, classes_count, total_classes = matcher.calculate_ratios(language, repo_name, repo_url, doc_url, pages)
    print("Methods found:", example_count)
    print("Total methods:", total_methods)
    print("Classes found:", classes_count)
    print("Total classes:", total_classes)
    if total_methods > 0:
        print(example_count / total_methods)
    if total_classes > 0:
        print(classes_count / total_classes)
    os.chdir("..")


if __name__ == '__main__':
    # Extract tasks and link code examples
    # inp = "https://stanfordnlp.github.io/CoreNLP/index.html"
    # task_extract_and_link(inp)

    # # https://github.com/ijl/orjson
    # task_extract_and_link("http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson")
    # # https://github.com/stleary/JSON-java
    # task_extract_and_link("http://web.archive.org/web/20211017224709/https://github.com/stleary/JSON-java")
    # task_extract_and_link("https://stanfordnlp.github.io/CoreNLP/ner.html")
    # task_extract_and_link("https://stanfordnlp.github.io/CoreNLP/cmdline.html")
    # # https://www.nltk.org/api/nltk.tag.html
    # task_extract_and_link("https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html")
    # # https://www.nltk.org/api/nltk.parse.html
    # task_extract_and_link("https://web.archive.org/web/20210417122335/https://www.nltk.org/api/nltk.parse.html")
    # task_extract_and_link("https://api.jquery.com/jQuery.get")
    # task_extract_and_link("https://reactjs.org/docs/components-and-props.html")

    # api_methods_examples("python", "orjson", "https://github.com/ijl/orjson.git", "https://github.com/ijl/orjson")
    # api_methods_examples("python", "nltk", "https://github.com/nltk/nltk.git", "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html")
    api_methods_examples("python", "requests", "https://github.com/psf/requests.git", "https://docs.python-requests.org/en/latest/")
