import json
import os
from string import Template
from typing import List

import pandas as pd
from bs4 import BeautifulSoup

from analyze_library.prioritize_api.heurictics.has_api_analysis import get_all_posts
from analyze_library.prioritize_api.llm.create_prompt import get_few_shot_learning_prompt, get_zero_shot_learning_prompt
from analyze_library.prioritize_api.llm.detect_api_discussion import detect_api_discussion
from analyze_library.prioritize_api.llm.dtos.QueryMetadata import QueryMetadata
from analyze_library.prioritize_api.llm.dtos.modes import Modes
from analyze_library.prioritize_api.llm.util import get_query_metadata, save_result


def get_prompt_messages(library, api_fqn, post_body, mode: Modes):
    metadata: dict = {
        'library': library,
        'api_fqn': api_fqn,
        'post_body': post_body
    }

    messages = []

    if mode == Modes.ZERO_SHOT:
        messages: list[dict] = get_zero_shot_learning_prompt(metadata=metadata)

    elif mode == Modes.FEW_SHOT:
        messages: list[dict] = get_few_shot_learning_prompt(metadata=metadata)

    return messages


def get_text(post_body):
    soup = BeautifulSoup(post_body, "html.parser")

    return soup.text


def run_pipeline_temp(lib_name=""):
    # Small dataset to verify
    lib_name = 'numpy'
    api = 'numpy.save'

    posts = get_all_posts(lib_name)
    df = pd.DataFrame(posts)
    df_all_posts = df.drop_duplicates()

    post_ids = [30376581, 40219946, 35739839, 50816006, 47857782, 30811918, 45106398, 8955448, 17298129, 12713486,
                44697379, 37996295, 8361561, 43925624, 49258553]

    query_metadata_list = []

    for post_id in post_ids:
        post_body = df_all_posts[df_all_posts['post_id'] == str(post_id)]['body'].values[0]
        post_body = get_text(post_body)

        query_metadata_list.append(QueryMetadata(
            post_id=str(post_id),
            post=post_body,
            api=api,
            library=lib_name
        ))

    for query_metadata in query_metadata_list:
        prompt = get_prompt_messages(
            library=query_metadata.library,
            api_fqn=query_metadata.api,
            post_body=query_metadata.post,
            mode=Modes.FEW_SHOT
        )

        response = detect_api_discussion(prompt)

        save_result(query_metadata=query_metadata, query_result=response)

        print(f'{query_metadata.post}: {response}')


def run_pipeline(lib_name=""):

    query_metadata_list = get_query_metadata(library=lib_name)

    for query_metadata in query_metadata_list:
        prompt = get_prompt_messages(
            library=query_metadata.library,
            api_fqn=query_metadata.api,
            post_body=query_metadata.post,
            mode=Modes.FEW_SHOT
        )

        response = detect_api_discussion(prompt)

        save_result(query_metadata=query_metadata, query_result=response)

        print(f'{query_metadata.post}: {response}')


if __name__ == '__main__':
    run_pipeline("pandas")
