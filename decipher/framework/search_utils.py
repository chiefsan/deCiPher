'''
Functions used by deCiPher search
'''

from ..framework.schema import engine, Problem, InvertedIndex, TermDictionary
import sqlite3
import nltk
import string
from bs4 import BeautifulSoup
from os import listdir, sep
from os.path import join, isfile, exists
from time import time
from tabulate import tabulate
from collections import defaultdict
from sqlalchemy.orm import scoped_session, sessionmaker
from collections import defaultdict
import numpy as np


def preprocess_text(content: str) -> (list, list):
    '''
    Preprocesses the text.
    Performs stemming and tokenization. 
    Returns tokens without stopwords and their corresponding indices.
    '''

    # convert the entire content to lowercase
    content = content.lower()

    # tokenize using the function nltk.word_tokenize
    tokens = nltk.word_tokenize(content)

    # define the stopwords (not downloading it like normal using nltk.download
    # because there was an issue during heroku deployment (resolved now).
    # '$' and ',' are stopwords specifically in this domain (observed when viewing the database)
    stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]+[',', '$']
    
    # Use a masking technique to remove stopwords from tokens
    mask = list(map(lambda word: word not in stopwords, tokens))
    
    token_indices_no_stopwords = list(
        filter(lambda i: mask[i], range(len(tokens))))
    tokens_no_stopwords = [tokens[i] for i in token_indices_no_stopwords]
    
    # return tokens without stopwords and corresponding indices
    return tokens_no_stopwords, token_indices_no_stopwords


def search(query: str, max_num_results: int, session=scoped_session(sessionmaker(bind=engine)): sqlalchemy.orm.scoping.scoped_session) -> list:
    '''
    Returns the top `max_num_results` relevant results based on the query given
    '''
    
    # preprocess the query
    query,_ = preprocess_text(query)

    # find the total number of documents, which will be used when computing the 
    # inverse document frequency
    num_docs = int(list(session.execute('SELECT COUNT(*) from problem'))[0][0])

    # initialize scores, the list of relevance scores based on which the query 
    # results are displayed
    scores = defaultdict(float)

    # initialize query_tf, the list that maintains the term_frequency of the _query document_
    query_tf = defaultdict(int)

    # update query_tf based on term occurence
    for term in query:
        query_tf[term]+=1

    
    for term in query:
        # Find the row in the term dictionary corresponding to the current term
        term_dictionary_query = session.query(TermDictionary).filter_by(term=term).all()
        if len(term_dictionary_query)==0:
            # term not present in term dictionary
            continue
        # grab the term attributes
        term_id = term_dictionary_query[0].term_id
        inverted_index_query = session.query(InvertedIndex).filter_by(term_id=term_id).all()
        term_document_frequency = inverted_index_query[0].document_frequency
        term_tf_idf = query_tf[term]*np.log(num_docs/term_document_frequency)
        term_postings_list = eval(session.query(InvertedIndex).filter_by(term_id=term_id).all()[0].posting_list)
        
        # for each problem the term is present in, update the scores based on its frequency
        # in the document and the inverse document frequency
        for problem_id in term_postings_list:
            term_problem_tf = term_postings_list[problem_id]
            scores[problem_id]+=term_problem_tf*term_tf_idf

    # normalize the scores by dividing each element by the corresponding document length
    for problem_id in scores:
        problem_length = session.query(Problem).filter_by(problem_id=problem_id).all()[0].problem_length
        scores[problem_id] = scores[problem_id]/problem_length

    # sort the scores
    scores = sorted(scores, key=scores.get, reverse=True)

    # return the top scores
    return scores[:min(num_docs, max_num_results)]
