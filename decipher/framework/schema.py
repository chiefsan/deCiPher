"""
Interface to the SQL database.
Use SQLAlchemy to convert between DB tables and python objects.
"""
import os

from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc
from contextlib import contextmanager

from .db_config import DB_CONNECTION_STRING

Base = declarative_base()

class Problem(Base):
    __tablename__ = "problem"    
    problem_id = Column(String, primary_key=True, nullable=True)
    contest_id = Column(String, nullable=True)
    index = Column(String, nullable=True)
    title = Column(String, nullable=True)
    time_limit = Column(String, nullable=True)
    memory_limit = Column(String, nullable=True)
    input_file = Column(String, nullable=True)
    output_file = Column(String, nullable=True)
    statement = Column(String, nullable=True)
    input_specification = Column(String, nullable=True)
    output_specification = Column(String, nullable=True)
    sample_tests = Column(String, nullable=True)
    note = Column(String, nullable=True)

class InvertedIndex(Base):
    __tablename__= "inverted_index"
    term_id = Column(Integer, primary_key=True)
    term_frequency = Column(Integer)
    posting_list = Column(String)

class TermDictionary(Base):
    __tablename__ = "term_dictionary"
    term_id = Column(Integer, primary_key=True)
    term = Column(String, nullable=False)


engine = create_engine(DB_CONNECTION_STRING)

Base.metadata.create_all(engine)
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    db_session = sessionmaker(bind=engine, autoflush=False)
    session = db_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
