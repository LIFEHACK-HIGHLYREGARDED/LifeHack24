import requests
from bs4 import BeautifulSoup
import spacy
import stanza
import openai
stanza.install_corenlp(dir='C:\\NLP\\stanford-corenlp')
from stanza.server import CoreNLPClient
from neo4j import GraphDatabase

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
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "HighlyRegarded"))

    try:
        with driver.session() as session:
            for entity in entities:
                session.run("MERGE (:Entity {name: $name, type: $type})", name=entity[0], type=entity[1])
            
            for subj, rel, obj in relationships:
                session.run("MATCH (a:Entity {name: $subj}), (b:Entity {name: $obj}) "
                            "MERGE (a)-[:RELATION {type: $rel}]->(b)", subj=subj, rel=rel, obj=obj)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.close()


def translate_query_to_cypher(natural_language_query):
    openai.api_key = ''  # Make sure this is set correctly in your environment

    # Using the chat completion API which is suitable for chat models like "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Cypher query expert. Convert the following user question into a Cypher query."},
            {"role": "user", "content": natural_language_query}
        ]
    )

    # Extracting the Cypher query from the response
    cypher_query = response['choices'][0]['message']['content'].strip()
    return cypher_query

def run_neo4j_query(query):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "HighlyRegarded"))
    results = []
    try:
        with driver.session() as session:
            result = session.run(query)
            for record in result:
                results.append(record.data())  # Adjust data structure as needed
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.close()
    return results

def handle_user_query(user_query):
    # Convert natural language query to Cypher query
    cypher_query = translate_query_to_cypher(user_query)
    print("Generated Cypher Query:", cypher_query)

    # Execute the Cypher query in Neo4j
    results = run_neo4j_query(cypher_query)
    print("Results from Neo4j:", results)

    # Process and format the results for the user
    if not results:
        return "I couldn't find any information based on your query."
    else:
        # Example formatting: customize according to your data structure
        response = "Here's what I found:\n" + "\n".join([str(r) for r in results])
        return response

def extract_data(text):
    with CoreNLPClient(
            annotators=['openie'],
            timeout=30000,
            memory='4G',
            endpoint='http://localhost:9002',  # Ensure this is the correct port and it's not in use
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
text = "Microsoft acquires GitHub for $7.5 billion in 2018."

# Extract entities and relationships
entities, relationships = extract_data(text)
print("Extracted Entities:", entities)
print("Extracted Relationships:", relationships)

# Load extracted data into Neo4j
load_into_neo4j(entities, relationships)

# Example user query to find out who acquired GitHub
user_query = "What is Microsoft's relation with GitHub?"
cypher_query = translate_query_to_cypher(user_query)  # Assuming you have implemented this to return a valid Cypher query

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
