from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
import os


load_dotenv()


def wsgi_launch(environ, start_response):
    app = create_app()
    return app(environ, start_response)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="RSS_PLAYER")

    # Configure session for PKCE flow
    # In production, use secure cookies and proper session backend
    app.config["SESSION_COOKIE_SECURE"] = os.getenv("RSS_PLAYER_ENVIRONMENT", "dev") == "production"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SECRET_KEY"] = os.getenv("RSS_PLAYER_SECRET_KEY", "dev-secret-key")

    # Tell web browsers to specifically only allow our website to interact with this
    # API.
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    origin.strip()
                    for origin in app.config["ALLOWED_ORIGINS"].split(",")
                ],
            },
        },
        supports_credentials=True,
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
