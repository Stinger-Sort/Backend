from flask_login import UserMixin
from sort import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    score = db.Column(db.Float, default=0 ,nullable=False)

class TrashCan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longtitude = db.Column(db.Float, nullable=False)

    def __init__(self, id, weight, lat,lon):
        self.id = id
        self.weight = weight
        self.latitude = lat
        self.longtitude = lon