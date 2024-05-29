from dotenv import load_dotenv
from groq import Groq
import os
import requests
import pandas as pd

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)

source_code_url = 'https://raw.githubusercontent.com/windmill-labs/windmill-community-integrations/main/integrations/mailgun/Send_Email/script.bun.ts'

r = requests.get(source_code_url).text

# TODO: read the data from the jsonl file

def generate_zero_shot(task, api, lang, temperature=0.0, max_tokens=1024):
    res = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""
                You are a {lang} expert. 
                You generate integrations that allow users to access APIs using {lang}. 
                No explanations. Only the code.
                Make sure that you use the API that the user provides.
                Double-check the correctness of your code.
                """,
            },
            {
                "role": "user",
                "content": f'''
                Generate a script that can {task}. 
                You will be using the following API: {api}.
                ''',
            }
        ],
        model="llama3-70b-8192", #llama3-8b-8192
        temperature=temperature,
        max_tokens=max_tokens,
        #response_format= {"type": "json_object"}

        # IDEA: the LLM can return a JSON object with:
        # 1. The code for the integration
        # 2. The list of constants to be replaced (stuff to obtain: credentials, API keys, etc.)
    )
    return res.choices[0].message.content

def generate_few_shot(task, apis, lang, temperature=0.0, max_tokens=1024):
    res = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""
                You are a {lang} expert. 
                You generate integrations that allow users to access APIs. 
                No explanations.
                Make sure that you use the API that the user provides.
                Double-check the correctness of your code.
                Use this as an example: {r}.
                Remember: your code has to follow the same style. Do not deviate from this format.
                """,
            },
            {
                "role": "user",
                "content": f'''
                Generate a script that can {task}. 
                You will be using the following APIs: {apis}.
                ''',
            }
        ],
        model="llama3-70b-8192", #llama3-8b-8192
        temperature=temperature,
        max_tokens=max_tokens,
        #response_format= {"type": "json_object"}
    )
    return res.choices[0].message.content

if __name__ == "__main__":
    print(generate_zero_shot('Send an email', 'GMail', 'TypeScript'))
    print(10 * '*')
    print('FEW-SHOT')
    print(generate_few_shot('Send an email', 'GMail', 'TypeScript'))
