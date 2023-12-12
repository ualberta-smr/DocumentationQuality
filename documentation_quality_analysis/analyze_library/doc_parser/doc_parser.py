import html
import re
import ssl
from collections import deque
from multiprocessing.pool import ThreadPool
from typing import List
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

from analyze_library.doc_parser.doc_example_util import get_documentation_examples
from analyze_library.doc_parser.doc_signature_util import get_signatures_from_doc
from analyze_library.models.Signature import Signature
from analyze_library.models.doc_page import DocPage

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                  'AppleWebKit/537.11 (KHTML, like Gecko) '
                  'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}


def fetch_url(page_data):
    url = page_data[0]
    depth = page_data[1]
    response = None
    try:
        req = Request(url=url, headers=HEADERS)
        response = urlopen(req, context=ssl.SSLContext())
    except Exception as e:
        # if response:
        #     print(f'Failed to get response for: {url} with response code {response.code}')
        # else:
        #     print(f'Failed to get response for: {url}')
        #     print(e)
        return None
    return response, depth


def get_all_webpages(doc_home: str, max_depth: int) -> List[DocPage]:
    print("Getting pages up-to depth", max_depth)
    doc_pages: List[DocPage] = []
    stop_words = ['releasenotes', 'whatsnew', 'deprecated', 'community', 'updates', 'releasehistory', 'release-history',
                  'changes', 'license']

    dq = deque([[doc_home, 0]])

    request_batch = []
    batch_size = 100
    visited_links = set()
    while dq:
        page, depth = dq.popleft()

        if any(stop_word in page for stop_word in stop_words):
            continue

        request_batch.append([page, depth])
        if len(request_batch) < batch_size and dq:
            continue
        valid_requests = []
        for data in request_batch:
            page, depth = data[0], data[1]
            if depth <= max_depth:
                valid_requests.append((page, depth))
        if not valid_requests:
            continue
        responses = ThreadPool(min(batch_size, len(valid_requests))).imap_unordered(fetch_url, valid_requests)

        for response_data in responses:
            if response_data is None:
                continue
            response = response_data[0]
            depth = response_data[1]

            try:
                page_url = response.url
                content = html.unescape(response.read().decode("utf-8"))
                soup = BeautifulSoup(content, "html.parser")
                domain = urlparse(page_url).hostname
                if not domain:
                    # print("Invalid Link")
                    continue

                if page_url in [i.url for i in doc_pages]:
                    continue

                doc_page = DocPage(url=page_url, content=soup)
                doc_pages.append(doc_page)

                base_url = re.match(re.compile(".+\/"), page_url)[0]

                links = set(soup.find_all("a", href=True))
                links = [x for x in links if x not in visited_links]
                visited_links.update(links)

                for link in links:
                    href = link["href"]

                    # Redirecting to parent
                    if re.findall('.*\.\.\/.*', href):
                        continue

                    # Remove one or more './' from link
                    href = re.sub('(\.\/)*', '', href)

                    parse = urlparse(href)
                    # hostname is None means it is not an external site
                    # path not null means it is another path on the documentation
                    # not fragment means it does not have a "#"
                    # We do not want links with "#" because they're likely redundant
                    if parse.hostname is None:
                        if parse.path and not parse.fragment and not parse.query:
                            url = base_url + parse.path
                            if url not in [i[0] for i in dq] and url not in [x.url for x in doc_pages] and urlparse(
                                    url).hostname == urlparse(doc_home).hostname:
                                # print(url)
                                dq.append([url, depth + 1])
                    elif href not in [i[0] for i in dq] and href not in [x.url for x in doc_pages] \
                            and parse.hostname == domain and "#" not in href and \
                            urlparse(href).hostname == urlparse(doc_home).hostname:
                        # print(href)
                        dq.append([href, depth + 1])
            except Exception as e:
                pass
        request_batch.clear()

    return doc_pages


def get_functions_and_classes_from_doc_api_ref(doc_pages: List[DocPage]) -> List[Signature]:
    api_ref_keywords = ['api', 'reference', 'modules', 'module', 'generated', 'github']
    signatures: List[Signature] = []
    for page in doc_pages:
        if any(word in page.url for word in api_ref_keywords):
            signatures.extend(get_signatures_from_doc(page))

    if not signatures:
        for page in doc_pages:
            signatures.extend(get_signatures_from_doc(page))

    return signatures


def get_functions_and_classes_from_doc_examples(doc_pages: List[DocPage]) -> List:
    doc_examples: List = []

    for page in doc_pages:
        doc_examples.extend(get_documentation_examples(page))

    return doc_examples
