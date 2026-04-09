from flask import Blueprint, Flask, request
from flask_cors import CORS
import os

from rss_music_api_service import api_usage
from rss_music_api_service.errors import RequestError, get_error_response
from rss_music_api_service.logging_config import configure_logging
from rss_music_api_service.internal_apis import errors as db_errors


def wsgi_launch(environ, start_response):
    app = create_app()
    return app(environ, start_response)


def create_app() -> Flask:
    configure_logging()

    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="RSS_PLAYER")

    secret_key = os.getenv("RSS_PLAYER_SECRET_KEY")
    is_production = os.getenv("RSS_PLAYER_ENVIRONMENT", "production") == "production"

    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_COOKIE_SECURE"] = is_production
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = 3600
    app.config["SCRIPT_NAME"] = "/prod"

    if "API_ROOT" not in app.config:
        app.config["API_ROOT"] = "/"

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

    @app.before_request
    def before_all_requests():
        success = api_usage.use_api_tokens_for_endpoint(request.url_rule.rule)
        if not success:
            return get_error_response(RequestError.TOO_MANY_REQUESTS)

    @app.errorhandler(db_errors.InternalAPIBadResponseError)
    def handle_internal_bad_response(_error):
        return get_error_response(RequestError.INTERNAL_API_BAD_RESPONSE)

    @app.errorhandler(db_errors.InternalAPITransportError)
    def handle_internal_transport_error(_error):
        return get_error_response(RequestError.INTERNAL_API_TIMEOUT)

    return app


def apply_blueprints(app: Flask) -> None:
    from rss_music_api_service.routes.search import SEARCH_BP
    from rss_music_api_service.routes.link import LINK_BP
    from rss_music_api_service.routes.auth import AUTH_BP
    from rss_music_api_service.routes.playlists import PLAYLISTS_BP

    blueprints = [
        SEARCH_BP,
        LINK_BP,
        AUTH_BP,
        PLAYLISTS_BP,
    ]

    root_bp = Blueprint("root", __name__, url_prefix=app.config["API_ROOT"])

    for blueprint in blueprints:
        root_bp.register_blueprint(blueprint)

    app.register_blueprint(root_bp)
