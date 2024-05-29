from dotenv import load_dotenv
import os
from tavily import TavilyClient

load_dotenv()
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
client = TavilyClient(api_key=TAVILY_API_KEY)

def search(service):
    query_prompt = f'''
    Can I access the {service} API through their OpenAPI specification?
    If it does exist, your answer should provide only the link to the OpenAPI specification.
    If it does not, return `OpenAPI specification not found.` instead of the link.
    '''
    response = client.search(query=query_prompt, include_answer=True)
    assert response is not None
    return response['answer']

if __name__ == "__main__":
    print(search('Google Cloud'))
