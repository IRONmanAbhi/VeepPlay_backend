from flask import Flask
from VeePlay.config import Config
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import boto3
from datetime import timedelta

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
mail = Mail()
cors = CORS()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

    app.s3_client = boto3.client(
        "s3",
        aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=app.config["AWS_BUCKET_REGION"],
    )

    from VeePlay.main.routes import main
    from VeePlay.users.routes import users
    from VeePlay.content.routes import content

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(content)

    return app
