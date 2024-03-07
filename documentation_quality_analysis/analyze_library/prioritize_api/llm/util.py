import csv
import os
import re

import pandas as pd
from bs4 import BeautifulSoup

from analyze_library.prioritize_api.heurictics.has_api_analysis import get_all_posts
from analyze_library.prioritize_api.llm.dtos.QueryMetadata import QueryMetadata
from analyze_library.prioritize_api.llm.dtos.prompt_mode import PromptMode

CWD = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSE_PATH = os.path.join(ROOT_DIR, "query_responses")


def get_query_metadata(library) -> list[QueryMetadata]:
    query_metadata_list: list[QueryMetadata] = []

    try:
        path = os.path.join(CWD, f"prioritize_api/evaluation/libraries/{library}/discusses_api_ground_truth")

        all_posts = get_all_posts(library)
        df1 = pd.DataFrame(columns=['id', 'DISCUSSES_API'])

        with open(os.path.join(path, "selected_apis_for_ground_truth.csv")) as f:
            apis = f.read().split()

            for api in apis:

                data = pd.read_csv(os.path.join(path, f"{api}.csv"))
                df2 = data.loc[:, ['id', 'DISCUSSES_API']]
                ground_truth_df = pd.concat([df1, df2])

                df_all_posts = pd.DataFrame(all_posts)
                df_all_posts = df_all_posts.drop_duplicates()

                for post_id in list(ground_truth_df['id']):
                    post = df_all_posts[df_all_posts['post_id'] == str(post_id)]
                    post_title = post['title'].values[0]
                    post_body = post['body'].values[0]
                    post_body = get_text(post_body)

                    query_post = post_title + ":\n" + post_body

                    query_metadata_list.append(QueryMetadata(
                        post_id=str(post_id),
                        post=query_post,
                        api=api,
                        library=library
                    ))

        return query_metadata_list

    except Exception as e:
        return query_metadata_list


def save_result(query_metadata: QueryMetadata, query_result: str, run_count: str, mode: PromptMode = None):
    mode_directory = f'{mode.value}/{run_count}'
    if not os.path.exists(os.path.join(RESPONSE_PATH, f'{query_metadata.library}/{mode_directory}')):
        os.makedirs(os.path.join(RESPONSE_PATH, f'{query_metadata.library}/{mode_directory}'))

    dir_path = os.path.join(RESPONSE_PATH, f'{query_metadata.library}/{mode_directory}')

    with open(os.path.join(dir_path, f'{query_metadata.api}.csv'), 'a', newline='') as f:
        line = [[query_metadata.post_id, query_result]]

        writer = csv.writer(f)
        writer.writerows(line)


def get_text(post_body):
    soup = BeautifulSoup(post_body, "html.parser")

    return soup.text


def preprocess_response(response: str) -> bool:
    if get_word_match('Yes')(response):
        return True
    return False


def get_word_match(w):
    return re.compile(r'\b({0})\b'.format(w), re.IGNORECASE).search
