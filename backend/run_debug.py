from app.app import create_app

# When running this backend for production, use the flask module to execute this app and
# specifically tell it not to use debug mode. This bit of code will always use debug
# mode when this app is run as a script.
if __name__ == "__main__":
    print("Running backend in debug mode")
    app = create_app()
    app.run(debug=True)
