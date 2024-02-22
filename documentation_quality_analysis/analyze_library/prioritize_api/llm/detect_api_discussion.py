import os
# from dotenv import load_dotenv
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

# load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(2))
def detect_api_discussion(message):
    model = "gpt-3.5-turbo"

    completion = client.chat.completions.create(model=model,
    messages=[
        {
            "role": "user",
            "content": "\n\nThis is a test!",
        }
    ],
    temperature=0)
    logging.info(completion.usage.total_tokens)

    return completion.choices[0].message.content


detect_api_discussion("hi")