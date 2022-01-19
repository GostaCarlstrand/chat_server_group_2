from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# We will use a factory function to avoid cyclic imports
def create_app():
    app = Flask(__name__)
    # Many parts of flask will require us to use a secret key so we created one
    app.config['SECRET_KEY'] = 'myS3cr37k3y'
    # We will configure SQLAlchemy to use SQLite and the file db.sqlite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # Init the SQLAlchemy object with our app object
    db.init_app(app)

    from blueprints.open import bp_open
    app.register_blueprint(bp_open)

    from blueprints.user import bp_user
    app.register_blueprint(bp_user)

    return app
