from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

openai = OpenAI(api_key=SECRET_KEY)

def query_gpt_chat(messages):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages
    )
    return response

# Example usage
input_text = "What time did the incident happen?"
if SECRET_KEY:
    instructions = """
    Objective: You are a chatbot designed to provide information about terrorism-related incidents by accessing a detailed knowledge graph. 
    This graph has been populated with entities extracted from various reports and articles. These entities include people, objects, locations, and events related to specific terrorism incidents.

    Functionality: When presented with a question, you should reference the knowledge graph to provide accurate and relevant information. 
    The graph includes data from multiple sources and reports, ensuring comprehensive coverage of each incident. 
    You should synthesize information from across these reports to offer a concise and informed response.
    """

    chat_result = query_gpt_chat([{"role": "user", "content": instructions + input_text}])
    print("User: ", input_text)
    print("Response: ", chat_result.choices[0].message.content)
else:
    print("API key is not set.")