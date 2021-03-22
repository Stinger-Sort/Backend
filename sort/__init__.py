from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import datetime

from config import login, password, database

app = Flask(__name__)
app.secret_key = 'some secret'
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres://{login}:{password}@localhost/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = datetime.timedelta(days=1)

mail = Mail(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)

from sort import models, routes
db.create_all()
