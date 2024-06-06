import csv
import os
import re
from collections import Counter

import pandas as pd
from bs4 import BeautifulSoup

from analyze_library.prioritize_api.heurictics.has_api_analysis import get_all_posts
from analyze_library.prioritize_api.llm.dtos.QueryMetadata import QueryMetadata
from analyze_library.prioritize_api.llm.dtos.prompt_mode import PromptMode

CWD = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSE_PATH = os.path.join(ROOT_DIR, "query_responses")
RESULT_PATH = os.path.join(ROOT_DIR, "query_results")


def get_query_metadata(library) -> list[QueryMetadata]:
    query_metadata_list: list[QueryMetadata] = []

    try:
        post_per_api_file = os.path.join(CWD,
                                         f"prioritize_api/evaluation/libraries/{library}/{library}_post_per_api.csv")

        all_posts = get_all_posts(library)

        if len(all_posts) == 0:
            all_posts = get_all_so_posts_tagged_python()

        with open(post_per_api_file) as f:
            file_data = f.read().split()

            for row in file_data:
                api, post_id = row.split(',')

                if api == 'API':
                    continue

                df_all_posts = pd.DataFrame(all_posts)
                df_all_posts = df_all_posts.drop_duplicates()

                post = df_all_posts[df_all_posts['post_id'] == str(post_id)]
                if len(post) == 0:
                    continue

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


def get_all_so_posts_tagged_python():
    posts = []

    # path = os.path.join(CWD, f"stack_overflow_service/query_results/SO_posts_tagged_{lib_name}.csv")
    path = os.path.join(CWD, f"stack_overflow_service/query_results/SO_posts_tagged_python.csv")

    with open(path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                posts.append(row)
                line_count += 1

    return posts


def get_evaluate_query_metadata(library) -> list[QueryMetadata]:
    query_metadata_list: list[QueryMetadata] = []

    try:
        path = os.path.join(CWD, f"prioritize_api/evaluation/libraries/{library}/discusses_api_ground_truth")

        all_posts = get_all_posts(library)
        df1 = pd.DataFrame(columns=['id', 'DISCUSSES_API'])

        with open(os.path.join(path, "apis_for_ground_truth.csv")) as f:
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


def save_result(query_metadata: QueryMetadata, query_result: str, run_count: str):
    mode_directory = f'{run_count}'
    if not os.path.exists(os.path.join(RESPONSE_PATH, f'{query_metadata.library}/{mode_directory}')):
        os.makedirs(os.path.join(RESPONSE_PATH, f'{query_metadata.library}/{mode_directory}'))

    if not os.path.exists(os.path.join(RESULT_PATH, f'{query_metadata.library}/{mode_directory}')):
        os.makedirs(os.path.join(RESULT_PATH, f'{query_metadata.library}/{mode_directory}'))

    response_file_path = os.path.join(RESPONSE_PATH,
                                      f'{query_metadata.library}/{mode_directory}/discusses_api_response.csv')
    result_file_path = os.path.join(RESULT_PATH, f'{query_metadata.library}/{mode_directory}/discusses_api_result.csv')

    with open(response_file_path, 'a', newline='') as f:
        line = [[query_metadata.api, query_metadata.post_id, query_result]]

        writer = csv.writer(f)
        writer.writerows(line)

    with open(result_file_path, 'a', newline='') as f:
        result: bool = preprocess_response(query_result)
        line = [[query_metadata.api, query_metadata.post_id, result]]

        writer = csv.writer(f)
        writer.writerows(line)


def save_eval_result(query_metadata: QueryMetadata, query_result: str, run_count: str, mode: PromptMode = None):
    mode_directory = f'{mode.value}/{run_count}'
    if not os.path.exists(os.path.join(RESPONSE_PATH, f'{query_metadata.library}/eval/{mode_directory}')):
        os.makedirs(os.path.join(RESPONSE_PATH, f'{query_metadata.library}/eval/{mode_directory}'))

    dir_path = os.path.join(RESPONSE_PATH, f'{query_metadata.library}/eval/{mode_directory}')

    with open(os.path.join(dir_path, f'{query_metadata.api}.csv'), 'a', newline='') as f:
        line = [[query_metadata.post_id, query_result]]

        writer = csv.writer(f)
        writer.writerows(line)


def save_final_result(lib_name):
    counts = ['1', '2', '3']
    df = pd.DataFrame(columns=['API', 'post_id'])

    for count in counts:
        result_file_path = os.path.join(RESULT_PATH, f'{lib_name}/run{count}/discusses_api_result.csv')
        res_data = pd.read_csv(result_file_path, header=None)
        res_data.rename(columns={0: 'API', 1: 'post_id', 2: f'result{count}'}, inplace=True)

        if len(df) == 0:
            df = pd.concat([df, res_data])

        else:
            df[f'result{count}'] = res_data[f'result{count}']

    tot_len = len(df)

    i = 0
    while i < tot_len:
        values = df.iloc[i]
        post_id = values.post_id

        run_results = [values.result1, values.result2, values.result3]
        res_count = Counter(run_results)
        most_frequent: bool = res_count.most_common(1)[0][0]

        df.loc[df['post_id'] == post_id, ['final_result']] = most_frequent

        i += 1

    df.drop(['result1', 'result2', 'result3'], axis=1, inplace=True)

    df.to_csv(os.path.join(RESULT_PATH, f"{lib_name}/discusses_api_final_result.csv"), sep=',', index=False)


def get_text(post_body):
    soup = BeautifulSoup(post_body, "html.parser")

    return soup.text


def preprocess_response(response: str) -> bool:
    if get_word_match('Yes')(response):
        return True
    return False


def get_word_match(w):
    return re.compile(r'\b({0})\b'.format(w), re.IGNORECASE).search


def restructure_file(lib_name):
    CWD = os.getcwd()
    path = os.path.join(CWD, f"stats/{lib_name}_posts_ids_per_api.csv")

    # df = pd.read_csv(path, header=None)

    f = open(path, "r")

    # This assumes your spacing is arbitrary
    data = [line.split(',') for line in f]
    data = {line[0]: [item.strip() if item.strip() else None for item in line[1:]] for line in data}
    # The orient = "index" allows us to handle differing lengths of entries
    df = pd.DataFrame.from_dict(data, orient="index")
    df = df.dropna(axis=0, how='all')
    df = df.reset_index()

    final_df = pd.melt(df, id_vars=['index']).drop(['variable'], axis=1).dropna(axis=0, how='any').rename(
        columns={'index': 'API', 'value': 'post_id'})

    dest_path = os.path.join(CWD, f"prioritize_api/evaluation/libraries/{lib_name}/{lib_name}_post_per_api.csv")
    final_df.to_csv(dest_path, index=False)

    return dest_path


if __name__ == '__main__':
    save_final_result('boto3')
