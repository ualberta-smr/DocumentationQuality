import re

from nltk.tokenize import sent_tokenize, TweetTokenizer


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


# F K(S) = 206.835 − 1.015 words(S)/sentences(S) − 84.600 syllables(S)/words(S)

# Adapted from: https://github.com/cdimascio/py-readability-metrics/blob/master/readability/scorers/flesch.py
# Original by User: Carmine DiMascio
# Adapted by: Henry Tang on 09/09/2022 at 15:43 MDT
def find_text_readability_metrics(text):
    tokens = TweetTokenizer().tokenize(text)
    words = len(tokens)
    if words > 1:
        sentences = len(sent_tokenize(text))
        syllables = 0
        for token in tokens:
            syllables += count_syllables(token)

        score = 206.835 - (1.015 * (words/sentences)) - (84.600 * (syllables/words))
        # ease = get_rating(score)
        return score, None #, ease
    return None, None


def get_rating(score):
    if 90 <= score <= 100:
        ease = "very_easy"
    elif 80 <= score < 90:
        ease = "easy"
    elif 70 <= score < 80:
        ease = "fairly_easy"
    elif 60 <= score < 70:
        ease = "standard"
    elif 50 <= score < 60:
        ease = "fairly_difficult"
    elif 30 <= score < 50:
        ease = "difficult"
    else:
        ease = "confusing"
    return ease



