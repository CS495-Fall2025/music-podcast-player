import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    # Tell web browsers to specifically only allow our website to interact with this
    # API.
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    origin.strip() for origin in os.getenv("ALLOWED_ORIGINS").split(",")
                ],
            },
        },
    )

    apply_blueprints(app)

    return app


def apply_blueprints(app: Flask) -> None:
    from rss_music_backend.routes.search import SEARCH_BP

    blueprints = [
        SEARCH_BP,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
