import csv
import re

import numpy as np
import pandas as pd
from sklearn.metrics import recall_score, precision_score, f1_score, accuracy_score

from analyze_library.prioritize_api.heurictics.has_api_analysis import get_all_posts
from analyze_library.stack_overflow_service.summarization import get_text, get_summary_lexrank


def get_word_match(w):
    return re.compile(r'\b({0})\b'.format(w)).search


def find_if_api_discussed_full_name(api_name: str, post: str):
    # api_name = api_name.replace('.', '\.')

    if get_word_match(api_name)(post):
        return True

    return False


def find_if_api_discussed_name_components(api_name: str, post: str):
    last_component = api_name.split('.')[-1]
    last_components = last_component.replace('_', '.')

    if get_word_match(last_components)(post):
        return True

    return False


def get_post_discusses_api_result():
    posts = get_all_posts(lib_name)
    all_posts = pd.DataFrame(posts)
    all_posts.drop_duplicates(inplace=True)
    all_posts = all_posts.astype({'post_id': 'int'})

    with open(f"./libraries/{lib_name}/{lib_name}_sampled_apis.csv", "r") as f:
        apis = f.read().split()
        print(apis)

    # with open(f"./libraries/{lib_name}/{lib_name}_api.csv", "r") as f:
    #     apis = f.read().split()
    #     print(apis)

    for api in apis:
        data = pd.read_csv(f"./libraries/{lib_name}/discusses_api_ground_truth/{api}.csv")
        # bool(data.loc[data['id'] == '', 'DISCUSSES_API'].iloc[0])

        len = data['id'].size
        lexrank_summary = []
        LSA_summary = []
        GPT2_summary = []
        discusses_api_result = []

        for i in range(len):
            id = data['id'].iloc[i].item()

            post_body = all_posts[all_posts['post_id'] == id]['body'].item()

            title = all_posts[all_posts['post_id'] == id]['title'].item()
            original_text = get_text(post_body)
            original_text = title + ".\n" + original_text

            summary = get_summary_lexrank(original_text)
            summarized_text = ' '.join([str(i) for i in summary])
            # if title not in summarized_text:
            #     summarized_text = title + ". " + summarized_text
            lexrank_summary.append(summarized_text)

            discusses_api_result.append(find_if_api_discussed_full_name(api_name=api, post=summarized_text))

            # summary = get_summary_LSA(original_text)
            # LSA_summary.append(' '.join([str(i) for i in summary]))
            # summary = get_summary_gpt2(original_text)
            # GPT2_summary.append(' '.join([str(i) for i in summary]))

        data['discusses_api_result'] = discusses_api_result

        data['lexrank_summary'] = lexrank_summary
        # data['LSA_summary'] = lexrank_summary
        # data['GPT2_summary'] = lexrank_summary

        data.to_csv(f"./libraries/{lib_name}/heuristic_results/{api}.csv")


def evaluate_result():
    with open(f"./libraries/{lib_name}/{lib_name}_sampled_apis.csv", "r") as f:
        apis = f.read().split()
        print(apis)

    # with open(f"./libraries/{lib_name}/{lib_name}_api.csv", "r") as f:
    #     apis = f.read().split()
    #     print(apis)

    with open(f'./libraries/{lib_name}/overall_eval.csv', 'w', newline='') as f:

        result = [['API', 'Num Example', 'Recall', 'Accuracy', 'Precision', 'F-measure']]
        recalls = []
        precisions = []
        accuracies = []
        f_measures = []
        df1 = pd.DataFrame(columns=['DISCUSSES_API', 'discusses_api_result'])
        for api in apis:
            data = pd.read_csv(f"./libraries/{lib_name}/heuristic_results/{api}.csv")
            df2 = data.loc[:, ['DISCUSSES_API', 'discusses_api_result']]
            df1 = pd.concat([df1, df2])
            eval_data = []

            print("API:  " + api)
            eval_data.append("API " + api)

            recall = recall_score(data['DISCUSSES_API'], data['discusses_api_result'])
            print('Recall: ', recall)
            eval_data.append('Recall ' + str(recall))
            recalls.append(recall)

            precision = precision_score(data['DISCUSSES_API'], data['discusses_api_result'], zero_division=1)
            print('Precision: ', precision)
            eval_data.append('Precision ' + str(precision))
            precisions.append(precision)

            accuracy = accuracy_score(data['DISCUSSES_API'], data['discusses_api_result'])
            print('Precision: ', accuracy)
            eval_data.append('Accuracy: ' + str(accuracy))
            accuracies.append(accuracy)

            f_measure = f1_score(data['DISCUSSES_API'], data['discusses_api_result'], zero_division=1)
            print('F_measure: ', f_measure)
            eval_data.append('F_measure ' + str(f_measure))
            f_measures.append(f_measure)
            print()

            result.append([api, len(data), recall, accuracy, precision, f_measure])

        y_true = list(df1['DISCUSSES_API'])
        y = list(df1['discusses_api_result'])
        overall_recall = recall_score(y_true, y)
        overall_accuracy = accuracy_score(y_true, y)
        overall_precision = precision_score(y_true, y, zero_division=1)
        overall_f_measure = f1_score(y_true, y, zero_division=1)
        result.append(['Overall', len(df1), overall_recall, overall_accuracy, overall_precision, overall_f_measure])

        result.append(['Average', '', np.sum(recalls)/len(recalls),
                       np.sum(accuracies) / len(accuracies),
                       np.sum(precisions)/len(precisions),
                       np.sum(f_measures)/len(f_measures)])

        print('done')

        writer = csv.writer(f)
        writer.writerows(result)


if __name__ == '__main__':
    lib_name = "numpy"

    # get_post_discusses_api_result()

    evaluate_result()

