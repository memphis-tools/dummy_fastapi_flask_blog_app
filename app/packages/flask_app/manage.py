"""
Follow https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/
This Flask cli allows you to find and launch the Flask app for Gunicorn.
Through the app/packages/flask_app/project/__init__.py file.
"""

from flask.cli import FlaskGroup

from app.packages.flask_app.project import app

cli = FlaskGroup(app)


if __name__ == "__main__":
    cli()
