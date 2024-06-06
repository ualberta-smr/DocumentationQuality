import csv
import random

import pandas as pd
import os

from analyze_library.stack_overflow_service.stack_overflow_service import get_SO_posts_for_APIs_wo_eg


def get_random_apis(apis, lib_name):
    random_api = []

    for i in range(10):
        x = random.randint(1, 800)

        random_api.append([apis[x]])

    with open(f'{lib_name}/{lib_name}_sampled_apis_10.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(random_api)

    return random_api


CWD = os.getcwd()


def get_all_apis_wo_eg(lib_name):
    path = os.path.join(CWD, f"prioritize_api/evaluation/libraries/{lib_name}/{lib_name}_apis_wo_eg.csv")

    with open(path, 'r') as f:
        all_api_wo_eg = f.read()

    # with open(f'./libraries/{lib_name}/{lib_name}_all_apis', 'r') as f:
    #     all_api_wo_eg = f.read()

    all_api_wo_eg = all_api_wo_eg.split('\n')

    return all_api_wo_eg


def get_all_apis(lib_name):
    with open(f'./libraries/{lib_name}/{lib_name}_all_apis', 'r') as f:
        all_apis = f.read()

    all_apis = all_apis.split('\n')

    return all_apis


def get_sampled_apis(lib_name):
    with open(f'./{lib_name}/{lib_name}_sampled_apis.csv', 'r') as f:
        samples_apis = list(csv.reader(f, delimiter=","))

    return samples_apis


def get_post_ids(lib_name):
    with open(f'./{lib_name}/{lib_name}_posts_manual.csv', 'r') as f:
        # post_ids = list(csv.reader(f, delimiter=","))
        post_ids = f.read()
        post_ids = post_ids.split()

    return post_ids


def get_random_posts(posts, lib_name):
    random_posts = []
    random_posts_ids = []
    length = len(posts) - 1
    num_of_posts = 20

    for i in range(num_of_posts):
        x = random.randint(0, length)

        random_posts_ids.append([posts[x].get('post_id')])
        random_posts.append(posts[x])

    with open(f'{lib_name}/{lib_name}_posts_20.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(random_posts_ids)

    return random_posts


def get_all_posts(lib_name):
    posts = []

    try:

        path = os.path.join(CWD, f"stack_overflow_service/query_results/SO_posts_tagged_{lib_name}.csv")
        # path = os.path.join(CWD, f"stack_overflow_service/query_results/SO_posts_tagged_python.csv")

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

    except Exception as e:
        return posts


def find_SO_posts_for_APIs_wo_eg(lib_name):
    all_api_wo_eg = get_all_apis_wo_eg(lib_name)
    all_api_wo_eg = [api_without_empty for api_without_empty in all_api_wo_eg if api_without_empty]

    posts = get_all_posts(lib_name)

    df1 = pd.DataFrame(posts)
    df = df1.drop_duplicates()

    unique_posts = df.to_dict(orient='records')

    get_SO_posts_for_APIs_wo_eg(apis=all_api_wo_eg, lib_name=lib_name, posts=unique_posts)


def analyze_sampled_api_usage(lib_name):
    sampled_apis = get_sampled_apis(lib_name)

    posts = get_all_posts(lib_name)
    df1 = pd.DataFrame(posts)
    df = df1.drop_duplicates()
    # random_posts = get_random_posts(posts, lib_name)

    post_ids = get_post_ids(lib_name)

    sampled_posts = df[df['post_id'].isin(post_ids)].to_dict(orient='records')

    for api in sampled_apis:
        result = get_SO_posts_for_APIs_wo_eg(apis=[api], lib_name=lib_name, posts=sampled_posts)
        with open(f'libraries/results/{lib_name}/{api[0]}.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(result)


def analyze_single_api_usage(lib_name, api_name):
    posts = get_all_posts(lib_name)
    df1 = pd.DataFrame(posts)
    df = df1.drop_duplicates()

    unique_posts: list = df.to_dict(orient='records')

    get_SO_posts_for_APIs_wo_eg(apis=[api_name], lib_name=lib_name, posts=unique_posts)


if __name__ == '__main__':
    # library_name = 'numpy'
    library_name = 'requests'
    # library_name = 'requests'
    api_name = 'requests.Session.close'

    find_SO_posts_for_APIs_wo_eg(library_name)
    # analyze_sampled_api_usage(library_name)
    # analyze_single_api_usage(library_name, api_name)
