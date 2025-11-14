from apig_wsgi import make_lambda_handler

from rss_music_backend.app import create_app


lambda_handler = make_lambda_handler(create_app())
