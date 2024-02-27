import csv
import os

import numpy as np
import pandas as pd
from sklearn.metrics import recall_score, precision_score, accuracy_score, f1_score

from analyze_library.prioritize_api.llm.util import preprocess_response

CWD = os.getcwd()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSE_PATH = os.path.join(ROOT_DIR, "query_responses")
EVAL_DATA_PATH = os.path.join(ROOT_DIR, "evaluate")


def evaluate_result():
    library = "pandas"
    run_count = "run1"
    mode_directory = f"zero-shot/{run_count}"
    # mode_directory = f"few-shot/{run_count}"

    ground_truth_path = os.path.join(CWD, f"prioritize_api/evaluation/libraries/{library}/discusses_api_ground_truth")
    response_dir_path = os.path.join(RESPONSE_PATH, f'{library}/{mode_directory}')
    eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'{library}/{mode_directory}')

    results = [['API', 'Num Example', 'Recall', 'Accuracy', 'Precision', 'F-measure']]
    df_title = pd.DataFrame(columns=['id', 'DISCUSSES_API'])

    with open(os.path.join(ground_truth_path, "selected_apis_for_ground_truth.csv")) as f:
        apis = f.read().split()

    for api in apis:
        gt_data = pd.read_csv(os.path.join(ground_truth_path, f"{api}.csv"))
        df_values = gt_data.loc[:, ['id', 'DISCUSSES_API']]
        eval_df = pd.concat([df_title, df_values])
        eval_df["result"] = np.nan

        res_data = pd.read_csv(os.path.join(response_dir_path, f"{api}.csv"), names=['id', 'response'])

        for id in res_data['id'].values:
            print(id)
            response = res_data[res_data['id'] == id]['response'].values[0]

            result = preprocess_response(response)

            eval_df.loc[eval_df['id'] == id, ['result']] = result

        recall = recall_score(list(eval_df['DISCUSSES_API']), list(eval_df['result']))
        precision = precision_score(list(eval_df['DISCUSSES_API']), list(eval_df['result']), zero_division=1)
        accuracy = accuracy_score(list(eval_df['DISCUSSES_API']), list(eval_df['result']))
        f_measure = f1_score(list(eval_df['DISCUSSES_API']), list(eval_df['result']), zero_division=1)

        results.append([api, len(eval_df), recall, accuracy, precision, f_measure])

        eval_df.to_csv(os.path.join(eval_data_dir_path, f"{api}.csv"), sep=',')

    with open(os.path.join(eval_data_dir_path, "eval_result.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)


if __name__ == '__main__':
    evaluate_result()
