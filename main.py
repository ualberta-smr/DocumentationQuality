import html
import re
import os

from TaskExtractor import linker
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup


def read_page(url):
    req = Request(url=url, headers=linker.HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    domain_regex = re.compile(r"(?:https?://)([\w.]+)/")
    domain = re.search(domain_regex, url)
    if not domain:
        print("Invalid Link")
    os.chdir("TaskExtractor")
    link_directory = os.path.normpath("results/" + domain[1])
    if not os.path.exists(link_directory):
        os.mkdir(link_directory)
    # for link in soup.find_all("a", href=True):
    #     href = link["href"]
    #     if not re.search(re.compile("^#"), href):
    #         link_domain = re.search(domain_regex, href)
    #         if link_domain and link_domain[1] == domain[1]:
    #             linker.extract_and_link(href)
    linker.extract_and_link(url)
    if not os.listdir(link_directory):
        os.rmdir(link_directory)
    os.chdir("..")


if __name__ == '__main__':
    # read_page("https://stanfordnlp.github.io/CoreNLP/index.html")

    # https://github.com/ijl/orjson
    read_page("http://web.archive.org/web/20210831032333/https://github.com/ijl/orjson")
    # https://github.com/stleary/JSON-java
    read_page("http://web.archive.org/web/20211017224709/https://github.com/stleary/JSON-java")
    read_page("https://stanfordnlp.github.io/CoreNLP/ner.html")
    read_page("https://stanfordnlp.github.io/CoreNLP/cmdline.html")
    # https://www.nltk.org/api/nltk.tag.html
    read_page("https://web.archive.org/web/20210725152853/https://www.nltk.org/api/nltk.tag.html")
    # https://www.nltk.org/api/nltk.parse.html
    read_page("https://web.archive.org/web/20210417122335/https://www.nltk.org/api/nltk.parse.html")
    read_page("https://api.jquery.com/jQuery.get/")
    read_page("https://reactjs.org/docs/components-and-props.html")
