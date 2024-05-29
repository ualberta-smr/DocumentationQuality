# Import libraries
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DATA_PATH = os.path.join(ROOT_DIR, "evaluate")


def box_plot():
    final_mode_dirs = ['chain-of-thought', 'few-shot', 'zero-shot']
    for final_mode_dir in final_mode_dirs:
        final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dir}/final_result')

        data = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))
        y1 = list(data['Recall'])
        y2 = list(data['Accuracy'])
        y3 = list(data['Precision'])
        y4 = list(data['F-measure'])

        data = [y1, y2, y3, y4]

        # Create a box and whisker plot
        plt.boxplot(data, labels=['Recall', 'Accuracy', 'Precision', 'F-measure'])
        plt.savefig(os.path.join(final_eval_data_dir_path, f"{final_mode_dir}.png"), format="png")

        # Show the plot
        plt.show()


def matplotlib_grouped_box_plot(data_group1, data_group2, data_group3, data_group4):
    # --- Your data, e.g. results per algorithm:
    # data1 = [5, 5, 4, 3, 3, 5]
    # data2 = [6, 6, 4, 6, 8, 5]
    # data3 = [7, 8, 4, 5, 8, 2]
    # data4 = [6, 9, 3, 6, 8, 4]
    #
    # # --- Combining your data:
    # data_group1 = [data1, data2]
    # data_group2 = [data3, data4]

    # --- Labels for your data:
    labels_list = ['Recall', 'Accuracy', 'Precision', 'F-measure']
    xlocations = range(len(data_group1))
    width = 0.3
    symbol = 'r+'
    ymin = 0
    ymax = 10

    ax = plt.gca()
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels(labels_list, rotation=0)
    ax.grid(True, linestyle='dotted')
    ax.set_axisbelow(True)
    ax.set_xticks(xlocations)
    plt.xlabel('X axis label')
    plt.ylabel('Y axis label')
    plt.title('title')

    # --- Offset the positions per group:
    positions_group1 = [x - (width + 0.01) for x in xlocations]
    positions_group2 = xlocations
    positions_group3 = [x + (width + 0.01) for x in xlocations]
    positions_group4 = [x + 2 * (width + 0.01) for x in xlocations]

    plt.boxplot(data_group1,
                sym=symbol,
                labels=[''] * len(labels_list),
                positions=positions_group1,
                widths=width,
                #           notch=False,
                #           vert=True,
                #           whis=1.5,
                #           bootstrap=None,
                #           usermedians=None,
                #           conf_intervals=None,
                #           patch_artist=False,
                )

    plt.boxplot(data_group2,
                labels=labels_list,
                sym=symbol,
                positions=positions_group2,
                widths=width,
                #           notch=False,
                #           vert=True,
                #           whis=1.5,
                #           bootstrap=None,
                #           usermedians=None,
                #           conf_intervals=None,
                #           patch_artist=False,
                )

    plt.boxplot(data_group3,
                labels=labels_list,
                sym=symbol,
                positions=positions_group3,
                widths=width,
                #           notch=False,
                #           vert=True,
                #           whis=1.5,
                #           bootstrap=None,
                #           usermedians=None,
                #           conf_intervals=None,
                #           patch_artist=False,
                )

    plt.boxplot(data_group4,
                labels=labels_list,
                sym=symbol,
                positions=positions_group4,
                widths=width,
                #           notch=False,
                #           vert=True,
                #           whis=1.5,
                #           bootstrap=None,
                #           usermedians=None,
                #           conf_intervals=None,
                #           patch_artist=False,
                )

    plt.savefig('boxplot_grouped.png')
    plt.savefig('boxplot_grouped.pdf')  # when publishing, use high quality PDFs
    plt.show()


def matplotlib_plot():
    final_mode_dirs = ['chain-of-thought', 'few-shot', 'zero-shot']

    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dirs[0]}/final_result')
    data_chain_of_thought = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))

    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dirs[1]}/final_result')
    data_few_shot = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))

    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dirs[1]}/final_result')
    data_zero_shot = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))

    data_group1 = [data_chain_of_thought['Recall'], data_few_shot['Recall'], data_zero_shot['Recall']]
    data_group2 = [data_chain_of_thought['Accuracy'], data_few_shot['Accuracy'], data_zero_shot['Accuracy']]
    data_group3 = [data_chain_of_thought['Precision'], data_few_shot['Precision'], data_zero_shot['Precision']]
    data_group4 = [data_chain_of_thought['F-measure'], data_few_shot['F-measure'], data_zero_shot['F-measure']]

    matplotlib_grouped_box_plot(data_group1, data_group2, data_group3, data_group4)


def sns_plot():
    final_mode_dirs = ['chain-of-thought', 'few-shot', 'zero-shot']

    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dirs[0]}/final_result')
    data_chain_of_thought = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))

    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dirs[1]}/final_result')
    data_few_shot = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))

    final_eval_data_dir_path = os.path.join(EVAL_DATA_PATH, f'pandas/{final_mode_dirs[2]}/final_result')
    data_zero_shot = pd.read_csv(os.path.join(final_eval_data_dir_path, "final_eval_result.csv"))

    data_chain_of_thought['prompt'] = 'chain_of_thought'
    data_chain_of_thought = data_chain_of_thought.drop(columns=['Num Example']).melt(id_vars=['API', 'prompt'],
                                                                                     var_name='Metric',
                                                                                     value_name='Score')

    data_few_shot['prompt'] = 'few_shot'
    data_few_shot = data_few_shot.drop(columns=['Num Example']).melt(id_vars=['API', 'prompt'], var_name='Metric',
                                                                     value_name='Score')

    data_zero_shot['prompt'] = 'zero_shot'
    data_zero_shot = data_zero_shot.drop(columns=['Num Example']).melt(id_vars=['API', 'prompt'], var_name='Metric',
                                                                       value_name='Score')

    new_df = pd.concat([data_chain_of_thought, data_few_shot, data_zero_shot])
    new_df.drop(['API'], axis=1)

    sns_grouped_box_plot(data=new_df)


def sns_grouped_box_plot(data):
    sns.color_palette("blend:#7AB,#EDA", as_cmap=True)
    ax = sns.boxplot(data=data,
                     x=data['Metric'],
                     y=data['Score'],
                     hue="prompt",
                     palette="pastel")
    sns.move_legend(ax, "lower center", bbox_to_anchor=(.5, 1), ncol=3, title=None, frameon=False)

    plt.savefig(os.path.join(EVAL_DATA_PATH, f"pandas/grouped_box_plot.png"), format="png", dpi=600)
    plt.show()


sns_plot()
