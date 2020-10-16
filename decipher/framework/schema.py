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
    p_id = Column(String, nullable=True)
    p_index = Column(String, nullable=True)
    p_title = Column(String, nullable=True)
    p_time_limit = Column(String, nullable=True)
    p_memory_limit = Column(String, nullable=True)
    p_input_file = Column(String, nullable=True)
    p_output_file = Column(String, nullable=True)
    p_statement = Column(String, nullable=True)
    p_input_specification = Column(String, nullable=True)
    p_output_specification = Column(String, nullable=True)
    p_sample_tests = Column(String, nullable=True)
    p_note = Column(String, nullable=True)

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
