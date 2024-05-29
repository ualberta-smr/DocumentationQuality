import csv
import os
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.metrics import recall_score, precision_score, accuracy_score, f1_score

from analyze_library.prioritize_api.llm.dtos.eval_scores import EvalScores
from analyze_library.prioritize_api.llm.util import preprocess_response

library = "pandas"
CWD = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSE_PATH = os.path.join(ROOT_DIR, "query_responses")
EVAL_DATA_PATH = os.path.join(ROOT_DIR, "evaluate")

ground_truth_path = os.path.join(CWD, f"prioritize_api/evaluation/libraries/{library}/discusses_api_ground_truth")


def evaluate_result():
    response_dir_path = os.path.join(RESPONSE_PATH, f'{library}/{mode_directory}')
    eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'{library}/{mode_directory}')

    if not os.path.exists(eval_data_dir_path):
        os.makedirs(eval_data_dir_path)

    results = [['API', 'Num Example', 'Recall', 'Accuracy', 'Precision', 'F-measure']]
    df_title = pd.DataFrame(columns=['id', 'DISCUSSES_API'])

    with open(os.path.join(ground_truth_path, "apis_for_ground_truth.csv")) as f:
        apis = f.read().split()

    all_dataset_df = pd.DataFrame()

    for api in apis:
        gt_data = pd.read_csv(os.path.join(ground_truth_path, f"{api}.csv"))
        df_values = gt_data.loc[:, ['id', 'DISCUSSES_API']]
        eval_df = pd.concat([df_title, df_values])
        eval_df["result"] = np.nan

        res_data = pd.read_csv(os.path.join(response_dir_path, f"{api}.csv"), names=['id', 'response'])

        for id in res_data['id'].values:
            print(id)
            response = res_data[res_data['id'] == id]['response'].values[0]

            result: bool = preprocess_response(response)

            eval_df.loc[eval_df['id'] == id, ['result']] = result

        eval_df.dropna(inplace=True)
        all_dataset_df = pd.concat([all_dataset_df, eval_df])

        eval_scores: EvalScores = get_eval_scores(y_true=list(eval_df['DISCUSSES_API']),
                                                  y_pred=list(eval_df['result']))

        results.append(
            [api, len(eval_df), eval_scores.recall, eval_scores.accuracy, eval_scores.precision, eval_scores.f_measure])

        eval_df.to_csv(os.path.join(eval_data_dir_path, f"{api}.csv"), sep=',')

    total_eval_score = get_eval_scores(y_true=list(all_dataset_df['DISCUSSES_API']),
                                       y_pred=list(all_dataset_df['result']))
    results.append(
        ['total_score', len(all_dataset_df), total_eval_score.recall, total_eval_score.accuracy,
         total_eval_score.precision, total_eval_score.f_measure])

    with open(os.path.join(eval_data_dir_path, "eval_result.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)


def get_eval_scores(y_true, y_pred):
    recall = recall_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=1)
    accuracy = accuracy_score(y_true, y_pred)
    f_measure = f1_score(y_true, y_pred)  # wil be zero if prediction = 0  and recall = 0
    return EvalScores(recall=recall, precision=precision, accuracy=accuracy, f_measure=f_measure)


def calculate_final_result():
    final_mode_dir = f"{prompt_technique}/final_result"
    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'{library}/{final_mode_dir}')

    if not os.path.exists(final_eval_data_dir_path):
        os.makedirs(final_eval_data_dir_path)

    with open(os.path.join(ground_truth_path, "apis_for_ground_truth.csv")) as f:
        apis = f.read().split()

    results = [['API', 'Num Example', 'Recall', 'Accuracy', 'Precision', 'F-measure']]

    for api in apis:
        gt_data = pd.read_csv(os.path.join(ground_truth_path, f"{api}.csv"))
        api_df = gt_data[['id', 'DISCUSSES_API']]
        count = 0

        while count < 3:
            count += 1

            mode_dir = f"{prompt_technique}/run{count}"
            eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'{library}/{mode_dir}')

            api_res_data = pd.read_csv(os.path.join(eval_data_dir_path, f"{api}.csv"))

            api_df[f'run{count}_result'] = api_res_data['result']

        api_df["final_result"] = np.nan
        tot_len = len(api_df)

        i = 0
        while i < tot_len:
            values = api_df.iloc[i]
            post_id = values.id

            run_results = [values.run1_result, values.run2_result, values.run3_result]
            res_count = Counter(run_results)
            most_frequent: bool = res_count.most_common(1)[0][0]

            api_df.loc[api_df['id'] == post_id, ['final_result']] = most_frequent

            i += 1

        api_df.to_csv(os.path.join(final_eval_data_dir_path, f"{api}.csv"), sep=',')

        eval_scores = get_eval_scores(y_true=list(api_df['DISCUSSES_API']),
                                      y_pred=list(api_df['final_result']))

        results.append(
            [api, len(api_df), eval_scores.recall, eval_scores.accuracy, eval_scores.precision, eval_scores.f_measure])

    with open(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)


if __name__ == '__main__':
    prompt_technique = "zero-shot"

    # run_count = "run3"
    # mode_directory = f"zero-shot/{run_count}"
    # mode_directory = f"few-shot/{run_count}"
    # mode_directory = f"chain-of-thought/{run_count}"

    run_count = 0

    # while run_count <= 3:
    #     run_count += 1
    #
    #     mode_directory = f"{prompt_technique}/run{run_count}"
    #     evaluate_result()

    calculate_final_result()
