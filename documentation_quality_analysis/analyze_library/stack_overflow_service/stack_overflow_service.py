import csv
import random
import re
from typing import List, Dict

import pandas as pd
from stackapi import StackAPI
from bs4 import BeautifulSoup

from analyze_library.models.Signature import Signature
from analyze_library.stack_overflow_service.SO_question import SOQuestions

SO_TAGS = {
    'requests': 'python;python-requests',
    'pandas': 'python;pandas',
    'numpy': 'python;numpy',
    'flask': 'python;flask',
    'nltk': 'python;nltk',
    'graphql compiler': 'python',
    'collections': 'python',
    'numba': 'python',
    'gitpython': 'python',
    'pyppeteer': 'python',
    'python-socketio': 'python',
    'scanpy': 'python',
    'bionumpy': 'python',
    'wikidata': 'python',
    'orjson': '',
    'mockito': ''
}


def get_so_question(item):
    so_ques = SOQuestions(
        question_id=item.get('post_id'),
        title=item.get('title'),
        body=item.get('body'),
        link=item.get('link'),
        tags=item.get('tags'),
        is_answered=item.get('is_answered'),
        answer_count=item.get('answer_count'),
        view_count=item.get('view_count'),
        score=item.get('score'),
        last_activity_date=item.get('last_activity_date'),
        creation_date=item.get('creation_date')
    )

    return so_ques


def get_SO_posts(lib_name, filter='!-MWWGgGi9_1e3AU1g)AXhbg55NTHxOeLY'):
    SITE = StackAPI('stackoverflow', key='c7m77CeXsNdKwnAYmCrIeg((')

    SITE.page_size = 100
    SITE.max_pages = 400

    tags = SO_TAGS.get(lib_name.lower())

    # filter created from here: https://api.stackexchange.com/docs/questions
    questions = SITE.fetch('questions',
                           tagged=tags, filter='!-MWWGgGi9_1e3AU1g)AXhbg55NTHxOeLY')

    items = questions.get('items')

    return items


def get_match_in_title(post: dict, api: str):
    title = post.get('title')
    if api in title:
        so_ques = get_so_question(post)
        return so_ques

    api_components = api.split('.')

    title_match_count = 0
    for comp in api_components:
        if get_word_match(comp)(title):
            title_match_count += 1

    title_match_ratio = title_match_count / len(api_components)

    if title_match_ratio > 0.7 and get_word_match(api_components[-1])(title):
        so_ques = get_so_question(post)
        return so_ques

    return None


def get_word_match(w):
    return re.compile(r'\b({0})\b'.format(w)).search


def get_match_in_body(post: dict, api: str):
    ques_body = post.get('body')
    soup = BeautifulSoup(ques_body, "html.parser")
    paragraphs = soup.find_all("p")
    pre_tags = soup.find_all("pre")
    hrefs = soup.find_all("a")

    found_in_href = False
    found_in_code = False
    found_in_code_snippet = False
    has_code_snippet = len(pre_tags) > 0

    matched_text = None

    for href in hrefs:
        # Search for simple name in href
        if api in href:
            found_in_href = True
            matched_text = api
            break

    for para in paragraphs:
        text = para.text

        # Search for fully qualified term in paragraph - text or code
        if get_word_match(api)(text):
            so_ques = get_so_question(post)
            return so_ques

        code_tags = para.find_all('code')
        # Search for simple name in code tags in the body's text
        for code in code_tags:
            if api == code.text:
                found_in_code = True
                break

        if found_in_code:
            break

    # Search for API usage in code snippet
    for pre in pre_tags:
        code_snippet = pre.find_all("code")
        if code_snippet:
            code_snippet = code_snippet[0].text

            if api + "(" in code_snippet:
                found_in_code_snippet = True

    # Look for the simple name in <code> tag or <href> tag in paragraph.
    # If a code snippet exists, then search for the use of the desired API in the code snippet.
    if has_code_snippet:
        if (found_in_href or found_in_code) and found_in_code_snippet:
            so_ques = get_so_question(post)
            return so_ques
    else:
        if found_in_href or found_in_code:
            so_ques = get_so_question(post)
            return so_ques

    return None


def get_mentions_in_stack_overflow(lib_name, apis: List[str], posts=None):
    if not posts:
        # posts = get_SO_posts(lib_name, filter='!-MWWGgGi9_1e3AU1g)AXhbg55NTHxOeLY')
        pass

    so_questions: Dict[str, List[SOQuestions]] = {}
    so_links: Dict[str, list] = {}

    match_details = [['id', 'has_api']]

    c = 0
    for post in posts:
        c += 1

        # if c > 5000:
        #     break
        link = post.get('link')

        for api in apis:
            match_found = False
            if api not in so_questions:
                so_questions[api] = []

            if link and api not in so_links:
                so_links[api] = []

            # SEARCH IN TITLE
            so_ques = get_match_in_title(post=post, api=api)
            if so_ques:
                so_questions[api].append(so_ques)
                print(f'{api} {so_ques.question_id}')
                match_details.append([post.get('post_id'), "TRUE"])
                match_found = True
                continue

            # SEARCH IN CODE and PARAGRAPH
            so_ques = get_match_in_body(post=post, api=api)
            if so_ques:
                so_questions[api].append(so_ques)
                print(f'{api} {so_ques.question_id}')
                match_details.append([post.get('post_id'), "TRUE"])
                match_found = True
                continue

            if not match_found:
                match_details.append([post.get('post_id'), "FALSE"])

    for api in so_questions:
        so_questions[api].sort(key=lambda x: x.score, reverse=True)

    with open("stats_new/SO_stats_" + lib_name + "_" + apis[0] + ".csv", "a") as f:
        for i in so_questions:
            line = f'{i}, {",".join([x.question_id for x in so_questions[i]])}'
            f.write(line)
            f.write("\n")

    return match_details


def analyze_SO_posts(apis, lib_name, posts):
    match_details = get_mentions_in_stack_overflow(lib_name=lib_name, apis=apis, posts=posts)

    return match_details


if __name__ == "__main__":
    apis = ['requests.Session.close']
    # mentions = get_mentions_in_stack_overflow(lib_name='flask', apis=apis, query_result="SO_posts_flask_")

    items = []
    with open('./query_results/SO_posts_flask.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                items.append(row)

            line_count += 1
        print(f'Processed {line_count} lines.')

    mentions = get_mentions_in_stack_overflow(lib_name='flask', apis=apis, posts=items)

    # print(mentions)
