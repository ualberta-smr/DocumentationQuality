import pandas as pd
from bs4 import BeautifulSoup

from analyze_library.prioritize_api.llm.create_prompt import get_few_shot_learning_prompt, \
    get_zero_shot_learning_prompt, get_chain_of_thought_learning_prompt
from analyze_library.prioritize_api.llm.detect_api_discussion import detect_api_discussion
from analyze_library.prioritize_api.llm.dtos.QueryMetadata import QueryMetadata
from analyze_library.prioritize_api.llm.dtos.prompt_mode import PromptMode
from analyze_library.prioritize_api.llm.util import get_evaluate_query_metadata, save_result, restructure_file, \
    get_query_metadata, save_final_result


def get_prompt_messages(library, api_fqn, post_body, mode: PromptMode):
    metadata: dict = {
        'library': library,
        'api_fqn': api_fqn,
        'post_body': post_body
    }

    messages = []

    if mode == PromptMode.ZERO_SHOT:
        messages: list[dict] = get_zero_shot_learning_prompt(metadata=metadata)

    elif mode == PromptMode.FEW_SHOT:
        messages: list[dict] = get_few_shot_learning_prompt(metadata=metadata)

    elif mode == PromptMode.CHAIN_OF_THOUGHT:
        messages: list[dict] = get_chain_of_thought_learning_prompt(metadata=metadata)

    return messages


def get_text(post_body):
    soup = BeautifulSoup(post_body, "html.parser")

    return soup.text


def run_evaluate_pipeline(lib_name, mode, run_count):
    query_metadata_list: list[QueryMetadata] = get_evaluate_query_metadata(library=lib_name)

    for query_metadata in query_metadata_list:
        prompt = get_prompt_messages(
            library=query_metadata.library,
            api_fqn=query_metadata.api,
            post_body=query_metadata.post,
            mode=mode
        )

        response = detect_api_discussion(prompt)

        save_result(query_metadata=query_metadata, query_result=response, run_count=run_count, mode=mode)

        print(f'{query_metadata.post_id}: {response}')


def run_pipeline(lib_name, mode, run_count):
    query_metadata_list: list[QueryMetadata] = get_query_metadata(library=lib_name)

    for query_metadata in query_metadata_list:
        prompt = get_prompt_messages(
            library=query_metadata.library,
            api_fqn=query_metadata.api,
            post_body=query_metadata.post,
            mode=mode
        )

        response = detect_api_discussion(prompt)

        save_result(query_metadata=query_metadata, query_result=response, run_count=run_count)

        print(f'{run_count} --> {query_metadata.post_id}: {response}')


def evaluate_discusses_api():
    modes = [PromptMode.ZERO_SHOT, PromptMode.FEW_SHOT, PromptMode.CHAIN_OF_THOUGHT]
    run_count = 0

    while run_count < 3:
        run_count += 1

        for mode in modes:
            run_evaluate_pipeline("pandas", mode=mode, run_count=f"run{run_count}")


def analyze_post_discusses_api(lib_name):
    mode = PromptMode.FEW_SHOT
    restructure_file(lib_name)

    run_count = 0

    while run_count < 3:
        run_count += 1
        run_pipeline(lib_name, mode=mode, run_count=f"run{run_count}")

    save_final_result(lib_name)

# analyze_post_discusses_api('boto3')
