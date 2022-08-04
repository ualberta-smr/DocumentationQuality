import html

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, element
from urllib.parse import urlparse

from util import HEADERS


def get_page(url):
    req = Request(url=url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")
    # has_search = find_search(soup)
    # has_toc = find_toc(soup)
    links_correct = check_hrefs(url, soup)
    return links_correct

def check_hrefs(url, soup):
    doc_home = urlparse(url).hostname
    links = soup.find_all("a", href=True)
    yes = []
    no =[]
    for link in links:
        parse = urlparse(link.attrs["href"])
        if "#" not in link.attrs["href"] and parse.hostname and doc_home != parse.hostname:
            no.append(link.attrs["href"])
        else:
            yes.append(link.attrs["href"])
    for i in yes:
        print(i)
    print()
    for i in no:
        print(i)
    return False



# sidebar "navigation", "sidebar", list with hrefs?
def find_toc(soup):
    has_toc = False
    if soup.find_all("div", {"class": "navigation"}) or soup.find_all("div", {"id": "sidebar"}):
        has_toc = True
    if not has_toc:
        lists = soup.find_all("ol") + soup.find_all("ul")
        for l in lists:
            count_items = 0
            count_links = 0
            for li in l.children:
                if isinstance(li, element.Tag):
                    for content in li.children:
                        if isinstance(content, element.Tag):
                            count_items += 1
                            if "href" in content.attrs:
                                count_links += 1
            if count_items == count_links:
                has_toc = True
                break
    return has_toc


def find_search(soup):
    has_search = False
    elements = soup.find_all("input")
    for ele in elements:
        element = None
        if "placeholder" in ele.attrs:
            if isinstance(ele.get("placeholder"), list):
                element = ele.get("placeholder")
            elif isinstance(ele.get("placeholder"), str):
                element = ele.get("placeholder").lower()
            if element and "search" in element:
                has_search = True
                break
    if not has_search:
        elements = soup.find_all("form")
        for ele in elements:
            if "class" in ele.attrs and "search" in ele.get("class"):
                has_search = True
                break
    return has_search


# type="search", class="...autocomplete..."

# <form class="search"

# <form class="searchform"
    # <span class="algolia-autocomplete"

# <span class="algolia-autocomplete"

# Just search for multiple things, like "input"

if __name__ == '__main__':
    urls = ["https://github.com/ijl/orjson",
            "https://github.com/stleary/JSON-java",
            "https://stanfordnlp.github.io/CoreNLP/",
            "https://web.archive.org/web/20210415060141/https://www.nltk.org/api/nltk.html",
            "https://api.jquery.com/",
            "https://reactjs.org/docs/getting-started.html",
            "https://github.com/jDataView/jBinary/wiki",
            "https://api.qunitjs.com/",
            "https://web.archive.org/web/20220505163814/https://docs.python-requests.org/en/latest/"]
    for url in urls:
        url = urls[2]
        print(url, get_page(url))
        break
