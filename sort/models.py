from sort import db


class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)


class UserBase(db.Model, Serializer):
    """Базовая модель с заработанными баллами"""
    __abstract__ = True
    name = db.Column(db.String(128))
    score = db.Column(db.Integer, default=0, nullable=False)

    # foreign key для изображения
    @declared_attr
    def profile_pic_id(cls):
        return db.Column(db.Integer, db.ForeignKey('img.id'))


class User(UserBase):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    score = db.Column(db.Float, default=0, nullable=False)
    profile_pic = db.relationship(
        "Img", backref=db.backref("Img", uselist=False))
    profile_pic_id = db.Column(db.Integer, db.ForeignKey('img.id'))


class Target(UserBase):
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))


class TrashCan(db.Model, Serializer):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, default=0)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    fullness = db.Column(db.Float, default=0)
    state = db.Column(db.Integer, default=100)
    state_user = db.Column(db.Integer, default=-1)
    key = db.Column(db.String, nullable=True)

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon


class History(db.Model, Serializer):
    """Запись о сдаче мусора"""
    id = db.Column(db.Integer, primary_key=True)

    trash_can = db.relationship(
        "TrashCan", backref=db.backref("TrashCan", uselist=False))
    trash_can_id = db.Column(db.Integer, db.ForeignKey('trash_can.id'))

    user = db.relationship("User", backref=db.backref("User", uselist=False))
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
