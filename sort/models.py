from sort import db
from sqlalchemy.ext.hybrid import hybrid_property
from sort.utils import level_counter


class Serializer(object):

    def serialize(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


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
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    city = db.Column(db.String(30))
    phone_number = db.Column(db.String(15))

    @hybrid_property
    def level(self):
        return level_counter(self.score)

    def serialize(self):
        record = {c.name: getattr(self, c.name)
                  for c in self.__table__.columns}
        del record['password']
        return record


class Organization(ScoreMixin):
    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(128))


class Target(ScoreMixin):
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))


class TrashCan(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, default=0)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    paper = db.Column(db.Float, default=0)
    glass = db.Column(db.Float, default=0)
    waste = db.Column(db.Float, default=0)
    fullness = db.Column(db.Float, default=0)
    state = db.Column(db.Integer, default=100)
    state_user = db.Column(db.Integer, default=-1)

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon


class History(db.Model, Serializer):
    """Запись о сдаче мусора"""
    id = db.Column(db.Integer, primary_key=True)

    trash_can_id = db.Column(db.Integer, db.ForeignKey('trash_can.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    paper = db.Column(db.Float, default=0)
    glass = db.Column(db.Float, default=0)
    waste = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    fullness = db.Column(db.Float, default=0)

    def __init__(self, user_id, trash_can_id, weight, paper, glass, waste):
        self.user_id = user_id
        self.trash_can_id = trash_can_id
        self.weight = weight
        self.paper = paper
        self.glass = glass
        self.waste = waste
