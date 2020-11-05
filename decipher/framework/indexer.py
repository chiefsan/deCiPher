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
from collections import defaultdict

def preprocess_text(content):
    content = content.lower()
    tokens = nltk.word_tokenize(content)
    stopwords = nltk.corpus.stopwords.words('english')+[',', '$']
    mask = list(map(lambda word: word not in stopwords, tokens))
    token_indices_no_stopwords = list(filter(lambda i: mask[i], range(len(tokens))))
    tokens_no_stopwords = [tokens[i] for i in token_indices_no_stopwords]

    return tokens_no_stopwords, token_indices_no_stopwords

from ..framework.schema import engine, Problem, InvertedIndex, TermDictionary

def preprocess_problems(session=scoped_session(sessionmaker(bind=engine))):
    for problem in session.query(Problem).all():
        print (problem.problem_id)
        textual_matter = problem.statement + problem.note + problem.title
        textual_matter, indices = preprocess_text(textual_matter)
        session.execute('UPDATE problem SET problem_length = "' + str(len(textual_matter)) + '" WHERE problem_id = ' + '"'+str(problem.problem_id) +'"')
        for term in textual_matter:
            if len(session.query(TermDictionary).filter_by(term=term).all())==0:
                next_id = len(session.query(TermDictionary).all())
                term_dict_element = TermDictionary()
                term_dict_element.term = term
                current_term_id = term_dict_element.term_id = next_id
                # print (current_term_id)
                session.add(term_dict_element)
                session.commit()
            else:
                current_term_id = session.query(TermDictionary).filter_by(term=term).all()[0].term_id
            query = session.query(InvertedIndex).filter_by(term_id=current_term_id).all()
            if len(query)==0:
                inverted_index_element = InvertedIndex()
                inverted_index_element.term_id = current_term_id
                inverted_index_element.posting_list = str(defaultdict(int)).replace("<class 'int'>", "int")
                inverted_index_element.term_frequency = 0
                inverted_index_element.document_frequency = 0
                session.add(inverted_index_element)
                session.commit()
            term_frequency = int(session.query(InvertedIndex).filter_by(term_id=current_term_id).all()[0].term_frequency)
            term_frequency += 1
            session.execute('UPDATE inverted_index SET term_frequency = "'+ str(term_frequency) + '" WHERE term_id = ' + str(current_term_id))
            posting_list = eval(session.query(InvertedIndex).filter_by(term_id=current_term_id).all()[0].posting_list)
            if posting_list[problem.problem_id]==0:
                document_frequency = int(session.query(InvertedIndex).filter_by(term_id=current_term_id).all()[0].document_frequency)
                document_frequency += 1
                session.execute('UPDATE inverted_index SET document_frequency = "'+ str(document_frequency) + '" WHERE term_id = ' + str(current_term_id))
                session.commit()
            posting_list[problem.problem_id] += 1
            session.execute('UPDATE inverted_index SET posting_list = "' + str(posting_list).replace("<class 'int'>", "int") + '" WHERE term_id = ' + str(current_term_id))
            session.commit()
    session.commit()
