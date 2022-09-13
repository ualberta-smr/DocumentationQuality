import html
import os
import subprocess
import traceback

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from .readability import find_text_readability_metrics, get_rating
from ..util import get_webpages, HEADERS


# Use same breakpoints of Flesch for readability here, the score is from 0-1, so treat same
def code_readability(page):
    scores = []
    try:
        req = Request(url=page, headers=HEADERS)
        content = html.unescape(urlopen(req).read().decode("utf-8"))
        soup = BeautifulSoup(content, "html.parser")
        examples = soup.find_all("pre")
        for example in examples:
            try:
                with open("Readability/temp.txt", "w", encoding="utf-8") as ex_file:
                    ex_file.write(example.get_text())
                result = subprocess.run(["javaw",
                                        "-jar",
                                        "Readability/rsm.jar",
                                        "Readability/temp.txt"],
                                       stdout=subprocess.PIPE)
                score = result.stdout.decode("ISO-8859-1").split()[-1]
                if score != "NaN":
                    scores.append(float(score))
                os.remove("Readability/temp.txt")
            except:
                pass
    except:
        pass

    return sum(scores)/len(scores) if len(scores) > 0 else None


def text_readability(page):
    scores = []
    # ease_count ={
    #     "very_easy": 0,
    #     "easy": 0,
    #     "fairly_easy": 0,
    #     "standard": 0,
    #     "fairly_difficult": 0,
    #     "difficult": 0,
    #     "confusing": 0
    # }
    try:
        req = Request(url=page, headers=HEADERS)
        content = html.unescape(urlopen(req).read().decode("utf-8"))
        soup = BeautifulSoup(content, "html.parser")
        paragraphs = soup.find_all("p")
        for paragraph in paragraphs:
            try:
                score, _ = find_text_readability_metrics(paragraph.get_text().strip())
                if score:
                    scores.append(score)
                    # ease_count[ease] += 1
            except:
                # paragraph.get_text()
                # traceback.print_exc()
                pass
    except:
        pass
    avg_score = sum(scores)/len(scores) if scores else None
    # most = (None, 0)
    # for key, value in ease_count.items():
    #     if value > most[1]:
    #         most = (key, value)
    return avg_score, None#, most[0]


def get_readability(library_name, language, doc_url):
    pages = get_webpages(doc_url, library_name)
    text_scores = []
    # text_ease = {
    #     "very_easy": 0,
    #     "easy": 0,
    #     "fairly_easy": 0,
    #     "standard": 0,
    #     "fairly_difficult": 0,
    #     "difficult": 0,
    #     "confusing": 0
    # }
    code_scores = []
    for page in pages:
        text_score, _ = text_readability(page)
        if language == "java":
            code_score = code_readability(page)
            if code_score:
                code_scores.append(code_score)
        if text_score:
            text_scores.append(text_score)
            # text_ease[ease] += 1

    avg_text_score = sum(text_scores)/len(text_scores) if len(text_scores) > 0 else None
    # most_freq_ease = (None, 0)
    # for key, value in text_ease.items():
    #     if value > most_freq_ease[1]:
    #         most_freq_ease = (key, value)
    avg_code_score = (sum(code_scores)/len(code_scores) * 100) if len(code_scores) > 0 else None
    return avg_text_score, get_rating(avg_text_score), avg_code_score, get_rating(avg_code_score)
