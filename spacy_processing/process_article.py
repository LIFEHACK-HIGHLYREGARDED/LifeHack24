def spacy_process(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(article_text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    for sent in doc.sents:
        print(sent.text)