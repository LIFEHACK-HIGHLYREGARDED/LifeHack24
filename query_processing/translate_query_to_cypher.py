import os
from openai import OpenAI
def translate_query_to_cypher(natural_language_query):

    openai = OpenAI(api_key=os.getenv('SECRET_KEY'))
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Cypher query expert. Convert the following user question into a Cypher query. An example of a valid prompt is:\nMATCH (m:Entity {name: \"Microsoft\"})-[r:RELATION]->(a)\nWHERE toLower(r.type) CONTAINS \"acquired\"\nRETURN a.name as CompanyAcquired\n"},
            {"role": "user", "content": natural_language_query}
        ]
    )

    # Extracting the Cypher query from the response
    print(response.choices[0].message.content.strip())
    cypher_query = response.choices[0].message.content.strip()
    return cypher_query