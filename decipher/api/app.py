from uuid import uuid4

from flask import Blueprint, Flask, session, request, jsonify
from flask_cors import CORS
from flask_session import Session
from decipher.api.exceptions import ApiException
from decipher.framework.api_utils import remove_db_session, create_response
from decipher.framework.search_utils import search
from sqlalchemy.orm import scoped_session, sessionmaker

import json

## Use a flask blueprint rather than creating the app directly
## so that we can also make a test app

blueprint = Blueprint("decipher", __name__)


@blueprint.errorhandler(ApiException)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@blueprint.teardown_request
def remove_session(ex=None):
    remove_db_session()


@blueprint.route("/")
def welcome():
    return create_response("Welcome to the decipher search API!<br/>")

# @blueprint.route("/api/search/<query>", defaults={'max_num_results': 5})
@blueprint.route("/api/search/<query>/<max_num_results>")
def welcome():
    results = search(query, max_num_results)
    return create_response("Welcome to the decipher search API!<br/>")

# @blueprint.route("/teams", methods=["GET"])
# def get_team_list():
#     """
#     Return a list of all teams for the current season
#     """
#     team_list = list_teams_for_api()
#     return create_response(team_list)


###########################################


def create_app(name=__name__):
    app = Flask(name)
    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = "blah"
    CORS(app, supports_credentials=True)
    app.register_blueprint(blueprint)
    Session(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5002, debug=True)
