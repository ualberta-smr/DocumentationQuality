import csv

import pandas as pd
from bs4 import BeautifulSoup
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer

from transformers import GPT2Tokenizer, GPT2LMHeadModel


def get_text(post_body):
    soup = BeautifulSoup(post_body, "html.parser")
    paragraphs = soup.find_all("p")
    texts = []
    for p in paragraphs:
        texts.append(p.text)

    return '\n'.join(texts)


def get_summary_lexrank(original_text):
    # Initializing the parser
    my_parser = PlaintextParser.from_string(original_text, Tokenizer('english'))

    # lex_rank_summarizer(document, sentences_count)
    # Creating a summary of 3 sentences.
    lex_rank_summarizer = LexRankSummarizer()
    lexrank_summary = lex_rank_summarizer(my_parser.document, sentences_count=2)

    # Printing the summary
    for sentence in lexrank_summary:
        print(sentence)

    return lexrank_summary


def get_summary_LSA(original_text):
    # Parsing the text string using PlaintextParser
    parser = PlaintextParser.from_string(original_text, Tokenizer('english'))

    # creating the summarizer
    lsa_summarizer = LsaSummarizer()
    lsa_summary = lsa_summarizer(parser.document, 2)

    # Printing the summary
    for sentence in lsa_summary:
        print(sentence)

    return lsa_summary


def get_summary_gpt2(original_text):
    # Instantiating the model and tokenizer with gpt-2
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    # Encoding text to get input ids & pass them to model.generate()
    inputs = tokenizer.batch_encode_plus([original_text], return_tensors='pt', max_length=512)
    summary_ids = model.generate(inputs['input_ids'], early_stopping=True)

    GPT_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    # print(GPT_summary)

    return GPT_summary

