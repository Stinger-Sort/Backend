from sort import db
from .serializer import Serializer


class TrashCan(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, default=0)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    full_paper = db.Column(db.Float, default=0)
    full_glass = db.Column(db.Float, default=0)
    full_waste = db.Column(db.Float, default=0)
    full_plastic = db.Column(db.Float, default=0)

    state = db.Column(db.Integer, default=100)
    state_user = db.Column(db.Integer, default=-1)

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon
