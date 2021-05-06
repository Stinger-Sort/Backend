from sort import db
from sqlalchemy.ext.hybrid import hybrid_property
from sort.utils import level_counter
from .serializer import Serializer
from .trash_can import TrashCan


class ScoreMixin(db.Model, Serializer):
    """Базовая модель с заработанными баллами"""
    __abstract__ = True
    name = db.Column(db.String(128))
    score = db.Column(db.Integer, default=0, nullable=False)


class User(ScoreMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    email_confirm = db.Column(db.String(128))
    city = db.Column(db.String(30))
    phone_number = db.Column(db.String(15))

    @hybrid_property
    def level(self):
        return level_counter(self.score)

    def serialize(self):
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns
                if c.name not in ('password', 'email_confirm')}


class Organization(ScoreMixin):
    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(128))


class Target(ScoreMixin):
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))


class History(db.Model, Serializer):
    """Запись о сдаче мусора"""
    id = db.Column(db.Integer, primary_key=True)

    trash_can_id = db.Column(db.Integer, db.ForeignKey('trash_can.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    paper = db.Column(db.Float, default=0)
    glass = db.Column(db.Float, default=0)
    waste = db.Column(db.Float, default=0)
    plastic = db.Column(db.Float, default=0)

    weight = db.Column(db.Float, default=0)

    def __init__(self, user_id, trash_can_id, weight, paper, glass, waste, plastic):
        self.user_id = user_id
        self.trash_can_id = trash_can_id
        self.plastic = plastic
        self.weight = weight
        self.paper = paper
        self.glass = glass
        self.waste = waste
        self.plastic = plastic
