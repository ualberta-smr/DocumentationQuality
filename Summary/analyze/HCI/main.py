import html
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from .checklist import find_search, find_toc, check_hrefs
from ..util import get_webpages, HEADERS


def run_checklist(library_name, doc_url):
    # pages = get_webpages(doc_url, library_name)
    # for page in pages:
    req = Request(url=doc_url, headers=HEADERS)
    content = html.unescape(urlopen(req).read().decode("utf-8"))
    soup = BeautifulSoup(content, "html.parser")

    has_search = find_search(soup)
    has_toc, has_start = find_toc(soup)
    links_correct = check_hrefs(doc_url, soup)

    return {
        "has_search": has_search,
        "has_toc": has_toc,
        "has_start": has_start,
        "links_correct": links_correct
    }
