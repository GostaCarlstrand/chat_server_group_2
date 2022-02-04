import dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwerty'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    db.init_app(app)
<<<<<<< HEAD
=======

    mqtt.init_app(app)


    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Server is connected to broker")
        else:
            print(f"Something went wrong, got {rc} status code")

>>>>>>> b927b26 (Start working on profile pciture)
    login_manager = LoginManager()

    # Init the login manager with our app object
    login_manager.init_app(app)

    # Create a user_loader function. Used by flask-login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.filter_by(id=user_id).first()

    from blueprints.open import bp_open
    app.register_blueprint(bp_open)

    from blueprints.user import bp_user
    app.register_blueprint(bp_user)

    from blueprints.api import bp_api
    app.register_blueprint(bp_api, url_prefix='/api/v1.0')

    return app


if __name__ == '__main__':
    dotenv.load_dotenv()
    app = create_app()
    app.run()
<<<<<<< HEAD
=======


>>>>>>> b927b26 (Start working on profile pciture)
