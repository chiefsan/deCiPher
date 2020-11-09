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


def preprocess_text(content: str) -> (list, list):
    """
    Preprocesses the text.
    Performs stemming and tokenization. 
    Returns tokens without stopwords and their corresponding indices.
    """

    # convert the entire content to lowercase
    content = content.lower()

    # tokenize using the function nltk.word_tokenize
    tokens = nltk.word_tokenize(content)

    # define the stopwords (not downloading it like normal using nltk.download
    # because there was an issue during heroku deployment (resolved now).
    # '$' and ',' are stopwords specifically in this domain (observed when viewing the database)
    stopwords = [
        "i",
        "me",
        "my",
        "myself",
        "we",
        "our",
        "ours",
        "ourselves",
        "you",
        "you're",
        "you've",
        "you'll",
        "you'd",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "he",
        "him",
        "his",
        "himself",
        "she",
        "she's",
        "her",
        "hers",
        "herself",
        "it",
        "it's",
        "its",
        "itself",
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "that'll",
        "these",
        "those",
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        "a",
        "an",
        "the",
        "and",
        "but",
        "if",
        "or",
        "because",
        "as",
        "until",
        "while",
        "of",
        "at",
        "by",
        "for",
        "with",
        "about",
        "against",
        "between",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "to",
        "from",
        "up",
        "down",
        "in",
        "out",
        "on",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "s",
        "t",
        "can",
        "will",
        "just",
        "don",
        "don't",
        "should",
        "should've",
        "now",
        "d",
        "ll",
        "m",
        "o",
        "re",
        "ve",
        "y",
        "ain",
        "aren",
        "aren't",
        "couldn",
        "couldn't",
        "didn",
        "didn't",
        "doesn",
        "doesn't",
        "hadn",
        "hadn't",
        "hasn",
        "hasn't",
        "haven",
        "haven't",
        "isn",
        "isn't",
        "ma",
        "mightn",
        "mightn't",
        "mustn",
        "mustn't",
        "needn",
        "needn't",
        "shan",
        "shan't",
        "shouldn",
        "shouldn't",
        "wasn",
        "wasn't",
        "weren",
        "weren't",
        "won",
        "won't",
        "wouldn",
        "wouldn't",
    ] + [",", "$"]

    # Use a masking technique to remove stopwords from tokens
    mask = list(map(lambda word: word not in stopwords, tokens))

    token_indices_no_stopwords = list(filter(lambda i: mask[i], range(len(tokens))))
    tokens_no_stopwords = [tokens[i] for i in token_indices_no_stopwords]

    # return tokens without stopwords and corresponding indices
    return tokens_no_stopwords, token_indices_no_stopwords


from ..framework.schema import engine, Problem, InvertedIndex, TermDictionary


def preprocess_problems(session=scoped_session(sessionmaker(bind=engine))) -> None:
    """
    Index the problems in the Problem table.
    """
    for problem in session.query(Problem).all():
        print(problem.problem_id)

        # extract the textual matter in the problem
        textual_matter = problem.statement + problem.note + problem.title

        # preprocess the textual matter
        textual_matter, indices = preprocess_text(textual_matter)

        # update the problem length
        session.execute(
            'UPDATE problem SET problem_length = "'
            + str(len(textual_matter))
            + '" WHERE problem_id = '
            + '"'
            + str(problem.problem_id)
            + '"'
        )
        for term in textual_matter:

            # find the term id
            if len(session.query(TermDictionary).filter_by(term=term).all()) == 0:
                # if term id does not exist, generate new term id and update the db
                next_id = len(session.query(TermDictionary).all())
                term_dict_element = TermDictionary()
                term_dict_element.term = term
                current_term_id = term_dict_element.term_id = next_id
                session.add(term_dict_element)
                session.commit()
            else:
                current_term_id = (
                    session.query(TermDictionary).filter_by(term=term).all()[0].term_id
                )

            # retrieve the entry of the term in the inverted index
            query = (
                session.query(InvertedIndex).filter_by(term_id=current_term_id).all()
            )
            if len(query) == 0:
                # if term is not present in inverted index, create new element
                inverted_index_element = InvertedIndex()
                inverted_index_element.term_id = current_term_id
                inverted_index_element.posting_list = str(defaultdict(int)).replace(
                    "<class 'int'>", "int"
                )
                inverted_index_element.term_frequency = 0
                inverted_index_element.document_frequency = 0
                session.add(inverted_index_element)
                session.commit()

            # update term frequency
            term_frequency = int(
                session.query(InvertedIndex)
                .filter_by(term_id=current_term_id)
                .all()[0]
                .term_frequency
            )
            term_frequency += 1
            session.execute(
                'UPDATE inverted_index SET term_frequency = "'
                + str(term_frequency)
                + '" WHERE term_id = '
                + str(current_term_id)
            )

            # update posting list
            posting_list = eval(
                session.query(InvertedIndex)
                .filter_by(term_id=current_term_id)
                .all()[0]
                .posting_list
            )
            if posting_list[problem.problem_id] == 0:
                # update document frequency the first time the term is encountered in a specific document (problem)
                document_frequency = int(
                    session.query(InvertedIndex)
                    .filter_by(term_id=current_term_id)
                    .all()[0]
                    .document_frequency
                )
                document_frequency += 1
                session.execute(
                    'UPDATE inverted_index SET document_frequency = "'
                    + str(document_frequency)
                    + '" WHERE term_id = '
                    + str(current_term_id)
                )
                session.commit()

            # update the posting list
            posting_list[problem.problem_id] += 1
            session.execute(
                'UPDATE inverted_index SET posting_list = "'
                + str(posting_list).replace("<class 'int'>", "int")
                + '" WHERE term_id = '
                + str(current_term_id)
            )
            session.commit()
    session.commit()
