import sqlite3
import nltk
import string
from bs4 import BeautifulSoup
from os import listdir, sep
from os.path import join, isfile, exists
from time import time
from tabulate import tabulate
from collections import defaultdict
from nltk.stem.snowball import EnglishStemmer  # Assuming we're working with English
from sqlalchemy.orm import scoped_session, sessionmaker


def preprocess_text(content):
    content = content.lower()
    tokens = nltk.word_tokenize(content)
    stopwords = nltk.corpus.stopwords.words('english')
    mask = list(map(lambda word: word not in stopwords, tokens))
    token_indices_no_stopwords = list(filter(lambda i: mask[i], range(len(tokens))))
    tokens_no_stopwords = [tokens[i] for i in token_indices_no_stopwords]

    return tokens_no_stopwords, token_indices_no_stopwords

from ..framework.schema import engine, Problem, InvertedIndex, TermDictionary
DBSESSION = scoped_session(sessionmaker(bind=engine))


def remove_db_session(dbsession=DBSESSION):
    dbsession.remove()

def preprocess_problems(session=DBSESSION):
    for problem in session.query(Problem).all():
        print (problem.problem_id)
        textual_matter = problem.statement + problem.note + problem.title
        textual_matter, indices = preprocess_text(textual_matter)
        for term in textual_matter:
            if len(session.query(TermDictionary).filter_by(term=term).all())==0:
                next_id = len(session.query(TermDictionary).all())+1
                term_dict_element = TermDictionary()
                term_dict_element.term = term
                current_term_id = term_dict_element.term_id = next_id
                session.add(term_dict_element)
                # session.commit()
            else:
                current_term_id = session.query(TermDictionary).filter_by(term=term).all()[0].term_id
            query = session.query(InvertedIndex).filter_by(term_id=current_term_id).all()
            if len(query)==0:
                inverted_index_element = InvertedIndex()
                inverted_index_element.term = term
                inverted_index_element.posting_list = '[0]'
                session.add(inverted_index_element)
                # session.commit()
            posting_list = eval(session.query(InvertedIndex).filter_by(term_id=current_term_id).all()[0].posting_list)
            if len(posting_list)>1 and posting_list[-1]==problem.problem_id:
                continue
            posting_list[0]+=1
            posting_list = str(posting_list + [problem.problem_id])
            session.execute('UPDATE inverted_index SET posting_list = "'+ posting_list + '" WHERE term_id = ' + str(current_term_id))
    session.commit()
