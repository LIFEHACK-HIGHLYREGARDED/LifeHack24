def spacy_process(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    # First, print out all detected entities and their labels
    print("Entities detected:")
    for ent in doc.ents:
        print(f"{ent.text} ({ent.label_})")

    print("\nPossible relationships:")
    # Analyze sentences for potential relationships between entities
    for sent in doc.sents:
        # For simplicity, use a dictionary to map entity start positions to the entity
        ent_map = {ent.start: ent for ent in sent.ents}

        # Iterate through tokens and look for possible verbs linking entities
        for token in sent:
            if token.dep_ in ('relcl', 'xcomp', 'ccomp', 'advcl', 'dobj', 'prep', 'pobj') and token.head in ent_map:
                # Subject of the verb could be a named entity
                subject = ent_map.get(token.head.i)
                # Object of the verb could be another named entity
                if token.dep_ in ('dobj', 'pobj') and token.head != token:
                    obj = ent_map.get(token.i)

                    # Check if both subject and object are entities and print the relationship
                    if subject and obj and subject != obj:
                        print(f"{subject.text} ({subject.label_}) {token.head.lemma_} {obj.text} ({obj.label_})")
            elif token.dep_ == 'appos' and token.head in ent_map:
                # Apposition can indicate a defining or renaming relation
                subject = ent_map.get(token.head.i)
                obj = ent_map.get(token.i)
                if subject and obj:
                    print(f"{subject.text} ({subject.label_}) is also known as {obj.text} ({obj.label_})")
article_text = "Apple Inc. is looking at buying U.K. startup for $1 billion. Tim Cook, the CEO of Apple, is leading the deal."
spacy_process(article_text)