import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS


load_dotenv()


def wsgi_launch(environ, start_response):
    app = create_app()
    return app(environ, start_response)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="RSS_PLAYER")

    # Tell web browsers to specifically only allow our website to interact with this
    # API.
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    origin.strip() for origin in app.config["ALLOWED_ORIGINS"].split(",")
                ],
            },
        },
    )

    apply_blueprints(app)

    return app


def apply_blueprints(app: Flask) -> None:
    from rss_music_backend.routes.search import SEARCH_BP
    from rss_music_backend.routes.auth import AUTH_BP

    blueprints = [
        SEARCH_BP,
        AUTH_BP,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
