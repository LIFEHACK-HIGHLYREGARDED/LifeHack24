def create_entities(tx, entities):
    for entity in entities:
        tx.run("MERGE (:Entity {name: $name, type: $type})", name=entity[0], type=entity[1])

def create_relationships(tx, relationships):
    for subj, rel, obj in relationships:
        tx.run("MATCH (a:Entity {name: $subj}), (b:Entity {name: $obj}) "
               "MERGE (a)-[:RELATION {type: $rel}]->(b)", subj=subj, rel=rel, obj=obj)

