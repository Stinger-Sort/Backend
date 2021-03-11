from flask_login import UserMixin
from sort import db, login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    score = db.Column(db.Float, default=0 ,nullable=False)

class TrashCan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)

    def __init__(self, id, weight):
        self.id = id
        self.weight = weight

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)