from urllib.parse import urlparse

from bs4 import element


def check_hrefs(url, soup):
    doc_home = urlparse(url).hostname
    links = soup.find_all("a", href=True)
    yes = []
    no = []
    for link in links:
        href = link.attrs["href"]
        parse = urlparse(href)
        if (parse.hostname and parse.hostname in doc_home) or (not parse.hostname and ("#" in href or "/" in href)):
            yes.append(href)
        else:
            no.append(href)
    # for i in yes:
    #     print(i)
    # print(len(yes))
    # print()
    # for i in no:
    #     print(i)
    # print(len(no))
    return bool(yes)


# sidebar "navigation", "sidebar", list with hrefs?
def find_toc(soup):
    has_toc = False
    has_start = False
    if soup.find_all("div", {"class": "navigation"}) or soup.find_all("div", {"id": "sidebar"}):
        has_toc = True
    if not has_toc:
        lists = soup.find_all("ol") + soup.find_all("ul")
        for l in lists:
            count_items = 0
            count_links = 0
            for li in l.children:
                if "quickstart" in li.text.lower() or "getting started" in li.text.lower():
                    has_start = True
                if isinstance(li, element.Tag):
                    for content in li.children:
                        if isinstance(content, element.Tag):
                            count_items += 1
                            if "href" in content.attrs:
                                count_links += 1
            if count_items == count_links:
                has_toc = True
                break
    return has_toc, has_start


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
