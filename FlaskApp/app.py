from flask import Flask

from board import pages

def create_app():
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app
# python -m flask --app board run --port 8000 --debug

if __name__ == "__main__":
    app = create_app()
    app.run(port=8000, debug=True)