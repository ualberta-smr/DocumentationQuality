import html
import re
import os

from TaskExtractor import linker
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from MethodExtractor import matcher


def get_webpages(doc_home):
    req = Request(url=doc_home, headers=linker.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    domain_regex = re.compile(r"(?:https?://)([\w.]+)/")
    domain = re.search(domain_regex, doc_home)
    if not domain:
        print("Invalid Link")

    pages = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if not re.search(re.compile("^#"), href):
            link_domain = re.search(domain_regex, href)
            if link_domain and link_domain[1] == domain[1]:
                pages.append(href)
    return domain[1], pages


def read_page(url):
    domain, pages = get_webpages(url)
    os.chdir("TaskExtractor")
    link_directory = os.path.normpath("results/" + domain)
    if not os.path.exists(link_directory):
        os.mkdir(link_directory)
    # Comment for loop and uncomment line underneath to use ground truth webpages
    # for page in pages:
    #     linker.extract_and_link(page)
    linker.extract_and_link(url)
    if not os.listdir(link_directory):
        os.rmdir(link_directory)
    os.chdir("..")


def task_extract_and_link(url):
    # read_page(url)

    # read_page("https://github.com/ijl/orjson")
    read_page("http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson")
    # read_page("https://github.com/stleary/JSON-java")
    read_page("http://web.archive.org/web/20211017224709/https://github.com/stleary/JSON-java")
    read_page("https://stanfordnlp.github.io/CoreNLP/ner.html")
    read_page("https://stanfordnlp.github.io/CoreNLP/cmdline.html")
    # https://www.nltk.org/api/nltk.tag.html
    read_page("https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html")
    # https://www.nltk.org/api/nltk.parse.html
    read_page("https://web.archive.org/web/20210417122335/https://www.nltk.org/api/nltk.parse.html")
    read_page("https://api.jquery.com/jQuery.get/")
    read_page("https://reactjs.org/docs/components-and-props.html")


def api_methods_examples(language, repo_url, doc_url):
    os.chdir("MethodExtractor")
    _, pages = get_webpages(doc_url)
    example_count = 0
    total_examples = 0
    classes_count = 0
    total_classes = 0
    for page in pages:
        try:
            a, b, c, d = matcher.calculate_ratios(language, repo_url, page)
            example_count += a
            total_examples += b
            classes_count += c
            total_classes += d
        except:
            pass
    print(example_count/total_examples)
    print(classes_count/total_classes)
    os.chdir("..")


if __name__ == '__main__':
    # Extract tasks and link code examples
    # url = "https://stanfordnlp.github.io/CoreNLP/index.html"
    # task_extract_and_link(url)
    api_methods_examples("python", "https://github.com/ijl/orjson.git", "https://github.com/ijl/orjson")
    # api_methods_examples("python", "https://github.com/nltk/nltk.git", "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html")

