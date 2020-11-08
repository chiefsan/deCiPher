from uuid import uuid4

from flask import Blueprint, Flask, session, request, jsonify
from flask_cors import CORS
from flask_session import Session
from decipher.api.exceptions import ApiException
from decipher.framework.api_utils import remove_db_session, create_response
from decipher.framework.search_utils import search
from sqlalchemy.orm import scoped_session, sessionmaker
from decipher.framework.schema import engine, Problem
from sqlalchemy import inspect
from flask import render_template


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


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
    return render_template('index.html')

@blueprint.route("/api/search/<query>", defaults={'max_num_results': 5})
@blueprint.route("/api/search/<query>/<max_num_results>")
def api_search(query, max_num_results, session=scoped_session(sessionmaker(bind=engine))):
    result = search(query, int(max_num_results))
    result_problems =  session.query(Problem).filter(Problem.problem_id.in_(tuple(result))).all()
    result_problems = list(map(object_as_dict, result_problems))
    # return create_response(result_problems)
    return render_template('default.html', problems=result_problems)

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
