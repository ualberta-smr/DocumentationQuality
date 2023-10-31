import re
from typing import List
from nltk.tokenize import sent_tokenize, TweetTokenizer

from analyze_library.models.doc_page import DocPage


def get_text_readability(webpages: List[DocPage]):
    try:
        text_scores = []
        for page in webpages:
            soup = page.content
            paragraphs = soup.find_all("p")
            # all_paragraph_texts = ' '.join(p.get_text(strip=True) for p in paragraphs)
            all_paragraph_texts = ' '.join(p.get_text(strip=True) for p in paragraphs if not  p.parent.name == 'li')
            score = get_text_readability_score(all_paragraph_texts)

            if score:
                text_scores.append(score)

        avg_text_score = sum(text_scores) / len(text_scores) if len(text_scores) > 0 else None

        return round(avg_text_score)
    except TypeError as e:
        print(e)
        return 0


# F K(S) = 206.835 − 1.015 words(S)/sentences(S) − 84.600 syllables(S)/words(S)

# Adapted from: https://github.com/cdimascio/py-readability-metrics/blob/master/readability/scorers/flesch.py
# Original by User: Carmine DiMascio
# Adapted by: Henry Tang on 09/09/2022 at 15:43 MDT
def get_text_readability_score(text):
    tokens = TweetTokenizer().tokenize(text)
    words = len(tokens)
    if words > 1:
        sentences = len(sent_tokenize(text))
        syllables = 0
        for token in tokens:
            syllables += count_syllables(token)

        score = 206.835 - (1.015 * (words / sentences)) - (84.600 * (syllables / words))
        return score
    return None


# Taken from: https://github.com/cdimascio/py-readability-metrics/blob/master/readability/text/syllables.py
# Written by user: Carmine DiMascio
# Taken by: Henry Tang on 09/09/2022 at 15:33 MDT
def count_syllables(word):
    word = word if type(word) is str else str(word)

    word = word.lower()

    if len(word) <= 3:
        return 1

    word = re.sub("(?:[^laeiouy]es|[^laeiouy]e)$", "", word)
    word = re.sub("^y", "", word)
    matches = re.findall("[aeiouy]{1,2}", word)
    return len(matches)
