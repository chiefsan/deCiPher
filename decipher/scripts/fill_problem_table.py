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


    k = 0
    while True:
        try:
            problem, remaining = grabJSON(s)
            p = Problem()
            p.p_contest_id = str(problem['p_id'])
            p.p_index = str(problem['p_index'])
            p.p_problem_id = str(problem['p_id'])+str(problem['p_index'])
            p.p_title = str(problem['p_title'])
            p.p_time_limit = str(problem['p_time_limit'])
            p.p_memory_limit = str(problem['p_memory_limit'])
            p.p_input_file = str(problem['p_input_file'])
            p.p_output_file = str(problem['p_output_file'])
            p.p_statement = str(problem['p_statement'])
            p.p_input_specification = str(problem['p_input_specification'])
            p.p_output_specification = str(problem['p_output_specification'])
            p.p_sample_tests = str(['p_sample_tests'])
            p.p_note = str(problem['p_note'])
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
