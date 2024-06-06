import json
import os
from string import Template
from typing import List

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MESSAGES_PATH = os.path.join(ROOT_DIR, "messages")
DATA_PATH = os.path.join(ROOT_DIR, "data")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "templates")


def get_few_shot_learning_prompt(metadata: dict) -> List[dict]:
    with open(os.path.join(DATA_PATH, "SO_post_example_set1.json")) as f:
        query_examples = json.load(f)
        metadata['example1'] = query_examples['example1']['post']
        metadata['answer1'] = query_examples['example1']['discusses_api']
        metadata['api1'] = query_examples['example1']['api']

        metadata['example2'] = query_examples['example2']['post']
        metadata['answer2'] = query_examples['example2']['discusses_api']
        metadata['api2'] = query_examples['example2']['api']

    with open(os.path.join(TEMPLATE_PATH, "few_shot_msg1_template.txt")) as f:
        message1 = f.read()
        message1 = Template(message1).substitute(metadata)
        metadata['message1'] = message1

    with open(os.path.join(TEMPLATE_PATH, "few_shot_msg2_template.txt")) as f:
        message2 = f.read()
        message2 = Template(message2).substitute(metadata)
        metadata['message2'] = message2

    with open(os.path.join(TEMPLATE_PATH, "few_shot_msg3_template.txt")) as f:
        message3 = f.read()
        message3 = Template(message3).substitute(metadata)
        metadata['message3'] = message3

    with open(os.path.join(MESSAGES_PATH, "few_shot_learning.json")) as f:
        message_template = json.load(f)
        messages = message_template['messages']

    for message in messages:
        message['content'] = Template(message['content']).substitute(metadata)

    return messages


def get_chain_of_thought_learning_prompt(metadata: dict) -> List[dict]:
    with open(os.path.join(DATA_PATH, "SO_post_example_set1.json")) as f:
        query_examples = json.load(f)
        metadata['example1'] = query_examples['example1']['post']
        metadata['thought1'] = query_examples['example1']['thoughts']
        metadata['api1'] = query_examples['example1']['api']

        metadata['example2'] = query_examples['example2']['post']
        metadata['thought2'] = query_examples['example2']['thoughts']
        metadata['api2'] = query_examples['example2']['api']

    with open(os.path.join(TEMPLATE_PATH, "chain_of_thought_msg1_template.txt")) as f:
        message1 = f.read()
        message1 = Template(message1).substitute(metadata)
        metadata['message1'] = message1

    with open(os.path.join(TEMPLATE_PATH, "chain_of_thought_msg2_template.txt")) as f:
        message2 = f.read()
        message2 = Template(message2).substitute(metadata)
        metadata['message2'] = message2

    with open(os.path.join(TEMPLATE_PATH, "chain_of_thought_msg3_template.txt")) as f:
        message3 = f.read()
        message3 = Template(message3).substitute(metadata)
        metadata['message3'] = message3

    with open(os.path.join(MESSAGES_PATH, "chain_of_thought_learning.json")) as f:
        message_template = json.load(f)
        messages = message_template['messages']

    for message in messages:
        message['content'] = Template(message['content']).substitute(metadata)

    return messages


def get_zero_shot_learning_prompt(metadata):
    with open(os.path.join(TEMPLATE_PATH, "zero_shot_template.txt")) as f:
        message = f.read()
        message = Template(message).substitute(metadata)
        metadata['message'] = message

    with open(os.path.join(MESSAGES_PATH, "zero_shot_learning.json")) as f:
        message_template = json.load(f)
        messages = message_template['messages']

        for message in messages:
            message['content'] = Template(message['content']).substitute(metadata)

    return messages
