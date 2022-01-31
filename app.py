import dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mqtt import Mqtt

db = SQLAlchemy()


mqtt = Mqtt()



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwerty'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['MQTT_BROKER_URL'] = '104.248.47.103'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_USERNAME'] = 'kyh_1'
    app.config['MQTT_PASSWORD'] = 'kyh1super2'
    db.init_app(app)

    mqtt.init_app(app)
    something = mqtt

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Server is connected to broker")
        else:
            print(f"Something went wrong, got {rc} status code")

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

    return app


if __name__ == '__main__':
    dotenv.load_dotenv()
    app = create_app()
    #mqtt.client.loop_start()
    app.run(port=5010)
    #mqtt.client.loop_stop()

