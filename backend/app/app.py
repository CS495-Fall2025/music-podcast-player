from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)

    # Tell web browsers to specifically only allow our website to interact with this API.
    # We will need to put the frontend's domain here later.
    CORS(
        app,
        resources={
            r"/*": {
                "origins": ["http://localhost:5173"],
            },
        },
    )

    apply_blueprints(app)

    return app


def apply_blueprints(app: Flask) -> None:
    from app.routes.math import MATH_BP

    blueprints = [
        MATH_BP,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
