from openai import OpenAI
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os

from LifeHack24.query_processing.translate_query_to_cypher import translate_query_to_cypher
from LifeHack24.query_processing.translate_results_to_english import translate_results_to_english

load_dotenv()
openai = OpenAI(api_key=os.getenv('SECRET_KEY'))

def run_neo4j_query(query):
    uri = os.getenv('URI')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    # Connect using the secure Bolt protocol with authentication
    driver = GraphDatabase.driver(uri, auth=(username, password))
    results = []

    try:
        with driver.session() as session:
            result = session.run(query)
            results = [record.data() for record in result]
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.close()

    return results

def handle_user_query(user_query):
    # Convert natural language query to Cypher query
    cypher_query = translate_query_to_cypher(user_query)
    '''
    cypher_query = """MATCH (m:Entity {name: "Microsoft"})-[r:RELATION]->(a)
    WHERE toLower(r.type) CONTAINS "acquired"
    RETURN a.name as CompanyAcquired"""
    '''
    print("Generated Cypher Query:", cypher_query)

    # Execute the Cypher query in Neo4j
    results = run_neo4j_query(cypher_query)
    print("Results from Neo4j:", results)

    # Process and format the results for the user
    if not results:
        return "I couldn't find any information based on your query."
    else:
        # Use GPT to translate results to English
        english_summary = translate_results_to_english(user_query, results)
        response = english_summary
        return response
    

def query_gpt_chat(messages):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages
    )
    return response

def refine_response(first_response):
    # This function takes the first call's response and formulates a new query to refine or elaborate the data.
    refine_instructions = """
    Based on the previous response, only output the entity list as a python list of pairwise-tuples with format (object name, object type), and the relationship list
    as a python list of 3-element tuples with format (subject, relation, object). No other additional texts including labels.
    """
    messages = [{"role": "user", "content": refine_instructions + first_response}]
    refined_response = query_gpt_chat(messages)
    return refined_response

def extract_data_gpt(text):
    if not os.getenv('SECRET_KEY'):
        print("API key is not set.")
    instructions = """
    Please provide information about terrorism-related incidents using a detailed knowledge graph. 
    This graph is populated with entities extracted from various reports and articles. These entities include people, objects, locations, and events specific to terrorism incidents.

    Strictly only output the following:
    1. One list of pair-tuples in the format <object name, object type> for entities.
    2. One list of 3-element tuples in the format <subject, relation, object> for representing relationships.

    Functionality: Utilize the knowledge graph to answer queries by synthesizing information from multiple sources to provide concise and accurate responses.
    """
    # First call to the API with initial instructions and input text
    chat_result = query_gpt_chat([{"role": "user", "content": instructions + text}])
    first_response = chat_result.choices[0].message.content
    print("First Call Response: ", first_response)

    # Second call to refine or elaborate on the first response
    refined_chat_result = refine_response(first_response)
    refined_response = refined_chat_result.choices[0].message.content
    print("Refined Call Response: ", refined_response)

# Example usage
text = "Steve Jobs is the founder of Apple, which makes revolutionary smartphones such as the brand new iPhone 15."
extract_data_gpt(text)
handle_user_query("Who is the founder of Apple?")
