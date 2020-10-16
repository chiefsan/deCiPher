"""
Fill the "problemset" table with the scraped data
"""
import simplejson
import os
import sys
import re

import json
from sqlalchemy import desc

# from ..framework.mappings import alternative_team_names, positions
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

    while True:
        problem, remaining = grabJSON(s)
        p = Problem()
        p.p_id = problem['p_id']
        p.p_index = problem['p_index']
        p.p_title = problem['p_title']
        p.p_time_limit = problem['p_time_limit']
        p.p_memory_limit = problem['p_memory_limit']
        p.p_input_file = problem['p_input_file']
        p.p_output_file = problem['p_output_file']
        p.p_statement = problem['p_statement']
        p.p_input_specification = problem['p_input_specification']
        p.p_output_specification = problem['p_output_specification']
        p.p_sample_tests = problem['p_sample_tests']
        p.p_note = problem['p_note']
        s = remaining
        session.add(p)
        if not remaining.strip():
            break
    session.commit()

def make_problem_table(session):

    filename = os.path.join(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "problemset.json",
        )
    )
    fill_problem_table_from_file(filename, session)


if __name__ == "__main__":
    with session_scope() as session:
        make_player_table(session)
