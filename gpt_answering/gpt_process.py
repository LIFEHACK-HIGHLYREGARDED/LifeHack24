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
input_text = "What is CS1231S"
if SECRET_KEY:
    instructions = "All your responses should be in the context of the National University of Singapore"
    chat_result = query_gpt_chat([{"role": "user", "content": input_text}])
    print("User: ", input_text)
    print("Response: ", chat_result.choices[0].message.content)
else:
    print("API key is not set.")