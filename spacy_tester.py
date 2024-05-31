import requests
from bs4 import BeautifulSoup
import spacy

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
    doc = nlp(article_text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
    for sent in doc.sents:
        print(sent.text)

url = "https://mothership.sg/2024/05/sq321-fell-54-3m-in-just-4-6-seconds/"
article_text = fetch_article_text(url)
spacy_process(article_text)
