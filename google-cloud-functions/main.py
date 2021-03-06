from flask import Flask, request
from google_cloud_function import execute

# Use for test only
def create_app():
    app = Flask(__name__)

    @app.route("/execute", methods=["POST"])
    def run():
        return execute(request)

    return app
