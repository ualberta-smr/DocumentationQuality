import os
from openai import OpenAI
import logging
# for exponential backoff
# based on openai doc https://platform.openai.com/docs/guides/rate-limits/error-mitigation?context=tier-one
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential
)

logging.basicConfig(level=logging.INFO)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(2))
def detect_api_discussion(messages):
    model = "gpt-3.5-turbo"

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    logging.info(response.usage.total_tokens)

    return response.choices[0].message.content
