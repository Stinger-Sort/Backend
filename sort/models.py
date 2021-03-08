from sort import db, login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))

class TrashCan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)

    def __init__(self, id, weight):
        self.id = id
        self.weight = weight

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)