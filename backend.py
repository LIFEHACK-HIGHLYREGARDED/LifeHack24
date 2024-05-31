#from LifeHack24.article_parsing.link_to_text import fetch_article_text
#from LifeHack24.spacy_processing.process_article import spacy_process
from article_parsing.link_to_text import fetch_article_text
from spacy_processing.process_article import spacy_process

def take_input(text):
    # Assuming links start with http
    if text.startswith('http'):
        article_text = fetch_article_text(text)
        print("Processing URL...")
    else:
        article_text = text
    spacy_process(article_text)


