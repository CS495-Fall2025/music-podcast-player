from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)

    # Tell web browsers to specifically only allow our website to interact with this API.
    # We will need to put the frontend's domain here later.
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5173"],
        },
    })

    apply_blueprints(app)

    return app


def apply_blueprints(app: Flask) -> None:
    from routes.time import time_blueprint

    app.register_blueprint(time_blueprint)


# When running this backend for production, use the flask module to execute this app and
# specifically tell it not to use debug mode. This bit of code will always use debug
# mode when this app is run as a script.
if __name__ == "__main__":
    print("Running backend in debug mode")
    app = create_app()
    app.run(debug=True)
