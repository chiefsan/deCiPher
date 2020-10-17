"""
Fill the "problemset" table with the scraped data
"""
import simplejson
import os
import sys
import re
import importlib 

import json
from sqlalchemy import desc
from bs4 import BeautifulSoup

from ..framework.schema import Problem, Base, engine

def fill_problem_table_from_file(filename, session):
    """
    use json file
    """
    FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
    WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)


    def grabJSON(s):
        """Takes the largest bite of JSON from the string.
        Returns (object_parsed, remaining_string)
        """
        decoder = simplejson.JSONDecoder()
        obj, end = decoder.raw_decode(s)
        end = WHITESPACE.match(s, end).end()
        return obj, s[end:]


    with open(filename) as f:
        s = f.read()
        s = s[1:-1].replace('}\n', '}').replace('\n{', '{').replace(',{', '{')

    example_problem = Problem()
    data_members = [attr for attr in dir(example_problem) if not callable(
        getattr(example_problem, attr)) and not attr.startswith("__")]
    k = 0
    while True:
        try:
            problem, remaining = grabJSON(s)
            p = Problem()
            p.contest_id = str(problem['p_id'])
            p.contest_id = BeautifulSoup(p.contest_id, 'lxml').get_text()
            p.index = str(problem['p_index'])
            p.index = BeautifulSoup(p.index, 'lxml').get_text()
            p.problem_id = str(problem['p_id'])+str(problem['p_index'])
            p.problem_id = BeautifulSoup(p.problem_id, 'lxml').get_text()
            p.title = str(problem['p_title'])
            p.title = BeautifulSoup(p.title, 'lxml').get_text()
            p.title = p.title[p.title.index(' ')+1:]
            p.time_limit = str(problem['p_time_limit'])
            p.time_limit = BeautifulSoup(p.time_limit, 'lxml').get_text()
            p.memory_limit = str(problem['p_memory_limit'])
            p.memory_limit = BeautifulSoup(p.memory_limi, 'lxml't).get_text()
            p.input_file = str(problem['p_input_file'])
            p.input_file = BeautifulSoup(p.input_file, 'lxml').get_text()
            p.output_file = str(problem['p_output_file'])
            p.output_file = BeautifulSoup(p.output_file, 'lxml').get_text()
            p.statement = str(problem['p_statement'])
            p.statement = BeautifulSoup(p.statement, 'lxml').get_text()
            p.input_specification = str(problem['p_input_specification'])
            p.input_specification = BeautifulSoup(p.input_specification, 'lxml').get_text()
            p.input_specification = p.input_specification[5:]
            p.output_specification = str(problem['p_output_specification'])
            p.output_specification = BeautifulSoup(p.output_specification, 'lxml').get_text()
            p.output_specification = p.output_specification[6:]
            p.sample_tests = str(problem['p_sample_tests'])
            p.sample_tests = BeautifulSoup(p.sample_tests, 'lxml').get_text()
            p.sample_tests = ''.join(eval(p.sample_tests))
            p.note = str(problem['p_note'])
            p.note = BeautifulSoup(p.note, 'lxml').get_text()
            p.note = eval(p.note)
            p.note =  re.sub(' {2,}', ' ', ' '.join(p.note))
            print(p.note )
            s = remaining
            session.add(p)
            k += 1
            if not remaining.strip():
                break
        except Exception as e:
            print("Error. Incorrect scraping. Please try again.", k, e)
            # print(s)
            break
    # s = open('/home/chiefsan/miniconda3/envs/airsenalenv/lib/python3.7/site-packages/decipher/data/problemset.json').read()
    print(k, 'problems added!')
    session.commit()
    print ('committed')

def make_problem_table(session):

    filename = os.path.join(
        os.path.join(
            os.path.dirname(importlib.util.find_spec('decipher').origin),
            "data",
            "problemset.json",
        )
    )
    fill_problem_table_from_file(filename, session)


if __name__ == "__main__":
    with session_scope() as session:
        make_player_table(session)
