import csv

import pandas as pd
import sumy
from bs4 import BeautifulSoup
# Importing the parser and tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
# Import the LexRank summarizer
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


if __name__ == '__main__':

    all_posts_df = pd.read_csv('./query_results/SO_posts_flask.csv')
    # flask_posts_df = pd.read_csv('./SO_stats_Flask.csv', names=list(range(75)))

    results = []
    with open('./SO_stats_Flask5000posts.csv', 'r') as f:
        rows = f.read().split('\n')
        row_c = 0
        for row in rows:
            row_c += 1

            if row_c > 5:
                print('here')

            count = 0
            cols = row.split(',')
            result = []
            for col in cols:
                if count == 0:
                    result.append(col)
                    results.append(result)
                elif col.strip():
                    result = ['', col]

                    post_id = col.split('/')[-1]
                    post_body = all_posts_df.loc[all_posts_df['post_id'] == int(post_id)].iloc[0]['body']
                    original_text = get_text(post_body)
                    result.append(original_text)

                    text_summary = get_summary_gpt2(original_text)
                    result.append(text_summary)
                    # result.append(' '.join([str(i) for i in text_summary]))
                    results.append(result)

                count += 1

            # results.append(result)

    with open('summary_gpt2_flask_5000posts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)
