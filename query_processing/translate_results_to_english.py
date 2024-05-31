from openai import OpenAI
import os

def translate_results_to_english(user_query, results):
    openai = OpenAI(api_key=os.getenv('SECRET_KEY'))
    prompt_text = "Based on this user query: " + user_query + "\n I have translated it into a cypher query and these are the results of the entities involved:\n" + str(results) + "\n"
    prompt_text += "Translate the following structured information into a clear English sentence to answer the user query appropriately:\n\n"


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant tasked with converting structured database outputs into clear English summaries. Please provide a summary of the following information:"},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=150,
        temperature=0.5  # Adjust temperature to control creativity
    )
    return response.choices[0].message.content.strip()