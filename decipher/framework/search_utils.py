from ..framework.schema import engine, Problem, InvertedIndex, TermDictionary
import sqlite3
import nltk
import string
from bs4 import BeautifulSoup
from os import listdir, sep
from os.path import join, isfile, exists
from time import time
from tabulate import tabulate
from collections import defaultdict # Assuming we're working with English
from nltk.stem.snowball import EnglishStemmer
from sqlalchemy.orm import scoped_session, sessionmaker


def preprocess_text(content):
    content = content.lower()
    tokens = nltk.word_tokenize(content)
    stopwords = nltk.corpus.stopwords.words('english')
    mask = list(map(lambda word: word not in stopwords, tokens))
    token_indices_no_stopwords = list(
        filter(lambda i: mask[i], range(len(tokens))))
    tokens_no_stopwords = [tokens[i] for i in token_indices_no_stopwords]

    return tokens_no_stopwords, token_indices_no_stopwords


DBSESSION = scoped_session(sessionmaker(bind=engine))

def remove_db_session(dbsession=DBSESSION):
    dbsession.remove()

def search(query, session=DBSESSION):
    vocabulary_size = int(list(session.execute('SELECT COUNT(*) from inverted_index'))[0][0])
    query_vector_tf = [0]*vocabulary_size
    query_vector_idf = [1]*vocabulary_size
    for term in query_vector:
        term_dictionary_query = session.query(TermDictionary).filter_by(term=term).all()
        if len(term_dictionary_query)==0:
            continue
        term_id = term_dictionary_query[0].term_id
        inverted_index_query = session.query(InvertedIndex).filter_by(term_id=term_id).all()
        term_document_frequency = inverted_index_query[0].posting_list[0]
        query_vector_tf[term_id] += 1
        query_vector_idf[term_id] = term_
