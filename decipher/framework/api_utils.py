from uuid import uuid4

from pandas import DataFrame
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Blueprint, Flask, session, request, jsonify
from decipher.framework.schema import engine


def remove_db_session(dbsession=scoped_session(sessionmaker(bind=engine))):
    """
    Removes given db session.
    """
    dbsession.remove()


def create_response(orig_response, dbsession=scoped_session(sessionmaker(bind=engine))):
    """
    Add headers to the response
    """
    response = jsonify(orig_response)
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept, x-auth",
    )
    return response
