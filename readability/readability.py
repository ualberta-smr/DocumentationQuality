# pip install py-readability-metrics
# python -m nltk.downloader punkt
from readability import Readability


# positive: number of blank lines/comments
# negative: line length, number of identifiers, preceding whitespace, number of keywords, number of parantheses/periods/commas
def find_code_readability_metrics():
    pass


# characters
def find_line_length(code):
    avg = 0
    m = 0
    return avg, m

# everything left of an "=" ?
def find_identifiers():
    avg = 0
    m = 0
    return avg, m

def preceding_whitespace():
    avg, m = 0
    return avg, m

def keywords():
    avg, m = 0
    return avg, m

def parantheses():
    avg = 0
    return avg

def periods():
    avg = 0
    return avg

def blank_lines():
    avg = 0
    return avg

def comments():
    avg = 0
    return avg

def commas():
    avg = 0
    return avg

# F K(S) = 206.835 − 1.015 words(S)/phrases(S) − 84.600 syllables(S)/words(S)
def find_text_readability_metrics():
    r = Readability("text")
    fk = r.flesch_kincaid()




def count_syllables(word):
    vowels = ["a", "e", "i", "o", "u"]
    syllable_count = 0
    syllables = []
    syllable = []
    last_was_vowel = False
    for c in word:
        vowel = False
        syllable.append(c)
        for v in vowels:
            if c == v:
                if not last_was_vowel:
                    syllable_count += 1
                vowel = True
                last_was_vowel = True
                break
        if vowel:
            syllables.append("".join(syllable))
            syllable = []
            last_was_vowel = False
    # if word[-2:] == "es" or word[-1] == "e":
    #     syllables -= 1
    return syllables, syllable_count