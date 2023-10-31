import html
import ssl
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from analyze_library.metric_calculation.navigability.hci_checklist_util import find_search, find_toc, \
    check_hrefs

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def get_navigability_score(doc_url: str):
    rating = None

    navigation_checklist = get_checklist_values(doc_url=doc_url)

    if navigation_checklist:
        count = 0
        for check in navigation_checklist.values():
            if check:
                count += 1
        if count > 2:
            rating = 5
        elif count > 1:
            rating = 3
        elif count > 0:
            rating = 1

    return rating


def get_checklist_values(doc_url):
    try:
        req = Request(url=doc_url, headers=HEADERS)
        response = urlopen(req, context=ssl.SSLContext())
        content = html.unescape(response.read().decode("utf-8"))
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

    except Exception:
        return None
