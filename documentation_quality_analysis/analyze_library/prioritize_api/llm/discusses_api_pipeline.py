import json
import os
from string import Template

import pandas as pd
from bs4 import BeautifulSoup

from analyze_library.prioritize_api.heurictics.has_api_analysis import get_all_posts
from analyze_library.prioritize_api.llm.detect_api_discussion import detect_api_discussion

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(ROOT_DIR, "templates")
DATA_PATH = os.path.join(ROOT_DIR, "data")


def get_prompt_messages(library, api_fqn, post_body, mode='one_shot'):
    metadata = {
        'library': library,
        'api_fqn': api_fqn,
        'post_body': post_body
    }

    with open(os.path.join(DATA_PATH, "discusses_api_example.txt")) as f:
        metadata['learning_example'] = f.read()

    if mode == 'one_shot':
        with open(os.path.join(TEMPLATE_PATH, "few_shot_learning.json")) as f:
            messages = json.load(f)

            messages['messages'][-1]['content'] = Template(messages['messages'][-1]['content']).substitute(metadata)

    return messages['messages']


def get_text(post_body):
    soup = BeautifulSoup(post_body, "html.parser")

    return soup.text


def run_pipeline():
    lib_name = 'numpy'
    api = 'numpy.save'

    posts = get_all_posts(lib_name)
    df = pd.DataFrame(posts)
    df_all_posts = df.drop_duplicates()

    post_ids = [30376581, 40219946, 35739839, 50816006, 47857782, 30811918, 45106398, 8955448, 17298129, 12713486,
                44697379, 37996295, 8361561, 43925624, 49258553]

    post_ids = [30376581, 30376581, 30376581, 30376581]

    for post_id in post_ids:
        post_body = df_all_posts[df_all_posts['post_id'] == str(post_id)]['body'].values[0]
        post_body = get_text(post_body)

        prompt = get_prompt_messages(
            library=lib_name,
            api_fqn=api,
            post_body=post_body,
            mode='one_shot'
        )

        response = detect_api_discussion(prompt)

        print(f'{post_id}: {response}')


if __name__ == '__main__':
    run_pipeline()
