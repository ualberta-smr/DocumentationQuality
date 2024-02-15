import json
import os
from string import Template
from typing import List

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_PATH = os.path.join(ROOT_DIR, "messages")
DATA_PATH = os.path.join(ROOT_DIR, "data")


def get_few_shot_learning_prompt(metadata: dict) -> List[dict]:
    with open(os.path.join(DATA_PATH, "SO_query_examples_set2.json")) as f:
        query_examples = json.load(f)
        metadata['example1'] = query_examples['example1']['post']
        metadata['answer1'] = query_examples['example1']['discusses_api']
        metadata['api1'] = query_examples['example1']['api']

        metadata['example2'] = query_examples['example2']['post']
        metadata['answer2'] = query_examples['example2']['discusses_api']
        metadata['api2'] = query_examples['example2']['api']

    with open(os.path.join(MESSAGES_PATH, "few_shot_learning.json")) as f:
        message_template = json.load(f)
        messages = message_template['messages']

        for message in messages:
            message['content'] = Template(message['content']).substitute(metadata)

    return messages


def get_zero_shot_learning_prompt(metadata):

    with open(os.path.join(MESSAGES_PATH, "zero_shot_learning.json")) as f:
        message_template = json.load(f)
        messages = message_template['messages']

        for message in messages:
            message['content'] = Template(message['content']).substitute(metadata)

    return messages
