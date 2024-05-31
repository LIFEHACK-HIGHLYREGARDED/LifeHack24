import requests
from bs4 import BeautifulSoup
import stanza
import openai
stanza.install_corenlp(dir='C:\\NLP\\stanford-corenlp')
from stanza.server import CoreNLPClient
from neo4j import GraphDatabase
import os

def fetch_article_text(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')

    # List of selectors to try (update this list based on common patterns you observe)
    selectors = [
        'div.article-content',
        'div.post-body',
        'div#main-content',
        'article',  # Some sites correctly use the article tag
        'div.content'
    ]

    article_text = ""
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            article_text = content.get_text(strip=True)
            break

    if not article_text:
        return "No article content found."
    return article_text


def load_into_neo4j(entities, relationships):
    uri = os.getenv('URI')
    username = os.getenv('USERNAME') 
    password = os.getenv('PASSWORD') 

    driver = GraphDatabase.driver(uri, auth=(username, password))

    try:
        with driver.session() as session:
            # Batch the creation of nodes and relationships for efficiency
            session.write_transaction(lambda tx: create_entities(tx, entities))
            session.write_transaction(lambda tx: create_relationships(tx, relationships))
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.close()

def create_entities(tx, entities):
    for entity in entities:
        tx.run("MERGE (:Entity {name: $name, type: $type})", name=entity[0], type=entity[1])

def create_relationships(tx, relationships):
    for subj, rel, obj in relationships:
        tx.run("MATCH (a:Entity {name: $subj}), (b:Entity {name: $obj}) "
               "MERGE (a)-[:RELATION {type: $rel}]->(b)", subj=subj, rel=rel, obj=obj)


def translate_query_to_cypher(natural_language_query):
    openai.api_key = os.getenv('SECRET_KEY')  # Make sure this is set correctly in your environment

    # Using the chat completion API which is suitable for chat models like "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Cypher query expert. Convert the following user question into a Cypher query. An example of a valid prompt is:\nMATCH (m:Entity {name: \"Microsoft\"})-[r:RELATION]->(a)\nWHERE toLower(r.type) CONTAINS \"acquired\"\nRETURN a.name as CompanyAcquired\n"},
            {"role": "user", "content": natural_language_query}
        ]
    )

    # Extracting the Cypher query from the response
    cypher_query = response['choices'][0]['message']['content'].strip()
    return cypher_query

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
    
def translate_results_to_english(user_query, results):
    """Translate results from structured data to English using GPT."""
    openai.api_key = os.getenv('SECRET_KEY')
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
    return response['choices'][0]['message']['content'].strip()

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
    if os.getenv('SECRET_KEY'):
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
    else:
        print("API key is not set.")

def extract_data(text):
    with CoreNLPClient(
            annotators=['openie'],
            timeout=30000,
            memory='4G',
            endpoint='http://localhost:9003',  # Ensure this is the correct port and it's not in use
            properties='english',
            be_quiet=True,
            classpath='C:\\NLP\\stanford-corenlp\\*') as client:

        ann = client.annotate(text)
        entities = set()
        relationships = []
        
        for sentence in ann.sentence:
            for triple in sentence.openieTriple:
                print(f"Subject: {triple.subject}, Relation: {triple.relation}, Object: {triple.object}")
                entities.add((triple.subject, 'Entity'))  # Assuming all subjects and objects are generic entities
                entities.add((triple.object, 'Entity'))
                relationships.append((triple.subject, triple.relation, triple.object))

        return list(entities), relationships


# Example usage
text = "Steve Jobs is the founder of Apple, which makes revolutionary smartphones such as the brand new iPhone 15."
extract_data_gpt(text)
'''
# Extract entities and relationships
entities, relationships = extract_data(text)
print("Extracted Entities:", entities)
print("Extracted Relationships:", relationships)

# Load extracted data into Neo4j
load_into_neo4j(entities, relationships)

# Example user query to find out who acquired GitHub
user_query = "Who is Steve Jobs?"
cypher_query = translate_query_to_cypher(user_query)  # Assuming you have implemented this to return a valid Cypher query
'''
cypher_query = """MATCH (m:Entity {name: "Microsoft"})-[r:RELATION]->(a)
WHERE toLower(r.type) CONTAINS "acquired"
RETURN a.name as CompanyAcquired"""
'''

# Execute the Cypher query and get results
results = run_neo4j_query(cypher_query)
response = handle_user_query(user_query)  # This function should format the response based on results

print("Cypher Query:", cypher_query)
print("Query Results from Neo4j:", results)
print("Response to User:", response)




#url = "https://mothership.sg/2024/05/sq321-fell-54-3m-in-just-4-6-seconds/"
#article_text = fetch_article_text(url)
#text1 = "Microsoft acquires GitHub for $7.5 billion. Tim Cook, CEO of Apple, advocates for privacy."
#spacy_process(text1)
#extract_relations(article_text)
#extract_relations(text1)
'''
