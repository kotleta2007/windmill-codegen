from dotenv import load_dotenv
from groq import Groq
import os
import requests

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)

source_code_url = 'https://raw.githubusercontent.com/windmill-labs/windmill-community-integrations/main/integrations/mailgun/Send_Email/script.bun.ts'

r = requests.get(source_code_url).text

def generate_zero_shot(action, description, api, lang, temperature=0.0, max_tokens=16384):
    res = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""
                You are a {lang} expert. 
                You generate integrations that allow users to access APIs using {lang}. 
                Make sure that you use the API that the user provides.
                Double-check the correctness of your code.

                Return a JSON.
                The JSON object should have the following properties:
                    - the code of the script, saved as a string.
                    - the appropriate filename for the script, saved as a string.
                    - additional explanations, saved as a string.
                """,
            },
            {
                "role": "user",
                "content": f'''
                Generate a script that can {action}. 
                It does it like this {description}.
                You will be using the following API: {api}.
                ''',
            }
        ],
        model="llama3-70b-8192", #llama3-8b-8192
        temperature=temperature,
        max_tokens=max_tokens,
        response_format= {"type": "json_object"}

        # IDEA: the LLM can return a JSON object with:
        # 1. The code for the integration
        # 2. The list of constants to be replaced (stuff to obtain: credentials, API keys, etc.)
    )
    return res.choices[0].message.content

def generate_few_shot(action, description, api, lang, temperature=0.0, max_tokens=16384):

    # TODO: add retry logic

    res = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""

                You are a {lang} expert. 
                You generate integrations that allow users to access APIs using {lang}. 
                Make sure that you use the API that the user provides.
                Double-check the correctness of your code.

                Return a JSON.
                The JSON object should have the following properties:
                    - the code of the script, saved as a string.
                    - the appropriate filename for the script, saved as a string.
                    - additional explanations, saved as a string.

                Use the following code as a reference:
                {r}
                """,
            },
            {
                "role": "user",
                "content": f'''
                Generate a script that can {action}. 
                Detailed description: {description}.
                You will be using the following API: {api}.

                ''',
            }
        ],
        model="llama3-70b-8192", #llama3-8b-8192
        temperature=temperature,
        max_tokens=max_tokens,
        response_format= {"type": "json_object"}
    )
    return res.choices[0].message.content

if __name__ == "__main__":
    print(generate_zero_shot('Send an email', 'Write an email and send it', 'Gmail', 'TypeScript'))
    print(10 * '*')
    print('FEW-SHOT')
    print(10 * '*')
    print(generate_few_shot('Send an email', 'Write an email and send it', 'Gmail', 'TypeScript'))
