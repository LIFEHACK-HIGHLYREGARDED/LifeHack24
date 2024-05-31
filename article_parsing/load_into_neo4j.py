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