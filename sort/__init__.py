from datetime import timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from config import login, password, database, mail_password

app = Flask(__name__)
app.secret_key = 'some secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/pavel/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sort.app.yar@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'sort.app.yar@gmail.com'
app.config['MAIL_PASSWORD'] = mail_password

mail = Mail(app)

db = SQLAlchemy(app)
jwt = JWTManager(app)

from sort import models, routes
db.create_all()
