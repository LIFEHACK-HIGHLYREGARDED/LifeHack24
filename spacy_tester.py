import requests
from bs4 import BeautifulSoup
import spacy
import stanza
stanza.install_corenlp(dir='C:\\NLP\\stanford-corenlp')
from stanza.server import CoreNLPClient

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


def spacy_process(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    print("Entities detected:")
    for ent in doc.ents:
        print(f"{ent.text} ({ent.label_})")

    print("\nTokens and Dependencies:")
    for sent in doc.sents:
        for token in sent:
            print(f"{token.text} ({token.dep_} -> {token.head.text})")

    print("\nPossible relationships:")
    for sent in doc.sents:
        ent_map = {ent.start: ent for ent in sent.ents}
        for token in sent:
            if token.dep_ in ('relcl', 'xcomp', 'ccomp', 'advcl', 'dobj', 'prep', 'pobj') and token.head.i in ent_map:
                subject = ent_map.get(token.head.i)
                obj = [ent for ent in sent.ents if ent.start == token.i]
                if obj:
                    obj = obj[0]
                    print(f"{subject.text} ({subject.label_}) {token.head.lemma_} {obj.text} ({obj.label_})")
            elif token.dep_ == 'appos' and token.head.i in ent_map:
                subject = ent_map.get(token.head.i)
                obj = [ent for ent in sent.ents if ent.start == token.i]
                if obj:
                    obj = obj[0]
                    print(f"{subject.text} ({subject.label_}) is also known as {obj.text} ({obj.label_})")

def extract_relations(text):
    # Initialize the CoreNLP client without automatically starting the server
    client = CoreNLPClient(
        annotators=['openie'],
        timeout=30000,
        memory='4G',
        endpoint='http://localhost:9001',
        properties='english',
        be_quiet=True,
        classpath='C:\\NLP\\stanford-corenlp\\*',
        start_server=False)  # Do not start the server automatically

    try:
        client.start()  # Manually start the server
        ann = client.annotate(text)
        for sentence in ann.sentence:
            for triple in sentence.openieTriple:
                print(f"Subject: {triple.subject}, Relation: {triple.relation}, Object: {triple.object}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.stop()  # Manually stop the server




url = "https://mothership.sg/2024/05/sq321-fell-54-3m-in-just-4-6-seconds/"
article_text = fetch_article_text(url)
text1 = "Microsoft acquires GitHub for $7.5 billion. Tim Cook, CEO of Apple, advocates for privacy."
spacy_process(text1)
#extract_relations(article_text)
extract_relations(text1)
