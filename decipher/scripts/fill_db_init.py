"""Script to fill the database after install."""
from .fill_problem_table import make_problem_table

from ..framework.schema import session_scope


def main():

    with session_scope() as session:
        make_problem_table(session)

        print("DONE!")
