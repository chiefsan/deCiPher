from uuid import uuid4

from flask_dance.contrib.google import make_google_blueprint, google
from flask import Blueprint, Flask, session, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from decipher.api.exceptions import ApiException
from decipher.framework.api_utils import remove_db_session, create_response
from decipher.framework.search_utils import search
from sqlalchemy.orm import scoped_session, sessionmaker
from decipher.framework.schema import engine, Problem
from sqlalchemy import inspect
from flask import render_template
from flask import current_app
from flask_restful import reqparse, abort, Api, Resource


import os
import json

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

# Use a flask blueprint rather than creating the app directly
# so that we can also make a test app

blueprint = Blueprint("decipher", __name__)


@blueprint.errorhandler(ApiException)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@blueprint.teardown_request
def remove_session(ex=None):
    """
    Remove db session.
    """
    remove_db_session()


@blueprint.route("/")
def welcome():
    """
    Return home page.
    """
    # if google.authorized:
    #     return render_template("index_logged_in.html", email=resp.json()["email"])
    # else:
    #     return render_template("index.html")
    if not google.authorized:
        return render_template("index.html")
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    return render_template("index_logged_in.html", email=resp.json()["email"])



@blueprint.route("/api/search/<query>", defaults={"max_num_results": 5})
@blueprint.route("/api/search/<query>/<max_num_results>")
def api_search(
    query: str, max_num_results: int, session=scoped_session(sessionmaker(bind=engine))
):
    """
    Show search results based on query and max_num_results.
    """
    result = search(query, int(max_num_results))
    result_problems = (
        session.query(Problem).filter(Problem.problem_id.in_(tuple(result))).all()
    )
    result_problems = list(map(object_as_dict, result_problems))
    if google.authorized:
        resp = google.get("/oauth2/v1/userinfo")
        assert resp.ok, resp.text
        return render_template("default_logged_in.html", email=resp.json()["email"], problems=result_problems)
    else:
        return render_template("default.html", problems=result_problems)


@blueprint.route("/login")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    assert resp.ok, resp.text
    return render_template("index_logged_in.html", email=resp.json()["email"])

@blueprint.route("/logout")
def logout():
    token = current_app.blueprints["google"].token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    del current_app.blueprints["google"].token  # Delete OAuth token from storage
    return render_template("index.html")


def abort_if_comment_doesnt_exist(comment_id):
    if comment_id not in COMMENTS:
        abort(404, message="comment {} doesn't exist".format(comment_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


# comment
# shows a single comment item and lets you delete a comment item
class comment(Resource):
    def get(self, comment_id):
        abort_if_comment_doesnt_exist(comment_id)
        return COMMENTS[comment_id]

    def delete(self, comment_id):
        abort_if_comment_doesnt_exist(comment_id)
        del COMMENTS[comment_id]
        return '', 204

    def put(self, comment_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        COMMENTS[comment_id] = task
        return task, 201


# commentList
# shows a list of all comments, and lets you POST to add new comments
class commentList(Resource):
    def get(self):
        return COMMENTS

    def post(self):
        args = parser.parse_args()
        comment_id = int(max(COMMENTS.keys()).lstrip('comment')) + 1
        comment_id = 'comment%i' % comment_id
        COMMENTS[comment_id] = {'task': args['task']}
        return COMMENTS[comment_id], 201

@blueprint.route("/api/commentspage")
def render_comments():
    out = []
    for comment in COMMENTS:
        temp = []
        temp.append(comment)
        temp.append(list(COMMENTS[comment].keys())[0])
        temp.append(list(COMMENTS[comment].values())[0])
        out.append(temp)
    out = out[::-1]
    if google.authorized:
        resp = google.get("/oauth2/v1/userinfo")
        assert resp.ok, resp.text
        return render_template("comments_logged_in.html", email=resp.json()["email"], comments=out)
    else:
        return render_template("comments.html", comments=out)


def create_app(name=__name__):
    """
    Create a Flask app.
    """
    app = Flask(name)
    app.config["SESSION_TYPE"] = "filesystem"
    app.secret_key = "blah"
    app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
    app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
    google_bp = make_google_blueprint(    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
)
    app.register_blueprint(google_bp, url_prefix="/login")
    CORS(app, supports_credentials=True)
    app.register_blueprint(blueprint)
    Session(app)
    return app


COMMENTS = {
    'comment1': {'task': 'wuuuuuuuuuuuuuuuuuuut. this is soooooooooooooooooo averaaaaaaaaaaaaaaaage'},
    'comment2': {'task': 'meeeeeeeeeeeeeeeh. this is sooooooo baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad'},
    'comment3': {'task': 'wooooooooooooooooooooooooooooooooooow. this is aweeeeeeeeesomeeeeeeeeeeeeeeeeeeeee!'},
}


if __name__ == "__main__":
    api = Api()
    api.add_resource(commentList, '/comments')
    api.add_resource(comment, '/comments/<comment_id>')
    app = create_app()
    api.init_app(app)
    app.run(host="127.0.0.1", port=5002, debug=True)
