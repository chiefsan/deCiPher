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
from collections import defaultdict
import numpy as np

def preprocess_text(content):
    content = content.lower()
    tokens = nltk.word_tokenize(content)
    stopwords = nltk.corpus.stopwords.words('english')+[',', '$']
    mask = list(map(lambda word: word not in stopwords, tokens))
    token_indices_no_stopwords = list(
        filter(lambda i: mask[i], range(len(tokens))))
    tokens_no_stopwords = [tokens[i] for i in token_indices_no_stopwords]

    return tokens_no_stopwords, token_indices_no_stopwords


DBSESSION = scoped_session(sessionmaker(bind=engine))

def search(query, max_num_results, session=DBSESSION):
    query,_ = preprocess_text(query)
    num_docs = int(list(session.execute('SELECT COUNT(*) from problem'))[0][0])
    scores = defaultdict(float)
    query_tf = defaultdict(int)
    for term in query:
        query_tf[term]+=1
    for term in query:
        term_dictionary_query = session.query(TermDictionary).filter_by(term=term).all()
        if len(term_dictionary_query)==0:
            continue
        term_id = term_dictionary_query[0].term_id
        inverted_index_query = session.query(InvertedIndex).filter_by(term_id=term_id).all()
        term_document_frequency = inverted_index_query[0].document_frequency
        term_tf_idf = query_tf[term]*np.log(num_docs/term_document_frequency)

        term_postings_list = eval(session.query(InvertedIndex).filter_by(term_id=term_id).all()[0].posting_list)
        for problem_id in term_postings_list:
            term_problem_tf = term_postings_list[problem_id]
            scores[problem_id]+=term_problem_tf*term_tf_idf
    for problem_id in scores:
        problem_length = session.query(Problem).filter_by(problem_id=problem_id).all()[0].problem_length
        scores[problem_id] = scores[problem_id]/problem_length
    scores = sorted(scores, key=scores.get, reverse=True)
    return scores[:min(num_docs, max_num_results)]
