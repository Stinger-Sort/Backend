from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import login, password, database


app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres://{login}:{password}@localhost/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from sort import models, routes
db.create_all()
