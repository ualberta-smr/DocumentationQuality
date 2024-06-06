import csv
import os

import pandas as pd


def save_SO_posts(lib_name, items: list):
    title = ['post_id', 'title', 'body', 'score', 'creation_date', 'tags', 'is_answered', 'view_count', 'answer_count',
             'last_activity_date', 'link']
    csv_list = [title]

    CWD = os.getcwd()
    path = os.path.join(CWD, "stack_overflow_service/query_results/SO_posts_tagged_" + lib_name + ".csv")

    for item in items:
        question_id = item['question_id']
        title = item['title']
        body = item['body']
        score = item['score']
        creation_date = item['creation_date']
        tags = ';'.join(item['tags'])
        is_answered = item['is_answered']
        view_count = item['view_count']
        answer_count = item['answer_count']
        last_activity_date = item['last_activity_date']
        link = item['link']

        item_list = [question_id, title, body, score, creation_date, tags, is_answered, view_count, answer_count,
                     last_activity_date, link]
        csv_list.append(item_list)

    with open(path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(csv_list)

    print("Saved SO posts at: " + path)

    return path


def get_all_posts(path):
    posts = []
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


# def analyze_api_usage(lib_name, path):
#     all_api_wo_eg = get_apis_wo_eg(lib_name)
#
#     posts = get_all_posts(lib_name)
#
#     df1 = pd.DataFrame(posts)
#     df = df1.drop_duplicates()
#
#     unique_posts = df.to_dict(orient='records')
#
#     analyze_SO_posts(apis=all_api_wo_eg, lib_name=lib_name, posts=unique_posts)


def get_apis_wo_eg(lib_name):
    CWD = os.getcwd()
    path = os.path.join(CWD,
                        f"analyze_library/prioritize_api/evaluation/libraries/{lib_name}/{lib_name}_apis_wo_eg.csv")

    with open(path, 'r') as f:
        apis_wo_eg = f.read()

    apis_wo_eg = apis_wo_eg.split('\n')

    return apis_wo_eg
