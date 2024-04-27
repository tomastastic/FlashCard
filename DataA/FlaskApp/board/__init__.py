from flask import Flask

def create_app():
    app = Flask(__name__)

    return app



# python -m flask --app board run --port 8000 --debug