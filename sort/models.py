from sort import db

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128))
    score = db.Column(db.Float, default=0, nullable=False)
    profile_pic = db.relationship(
        "Img", backref=db.backref("Img", uselist=False))
    profile_pic_id = db.Column(db.Integer, db.ForeignKey('img.id'))

class TrashCan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    paper = db.Column(db.Float, nullable=False)
    glass = db.Column(db.Float, nullable=False)
    waste = db.Column(db.Float, nullable=False)
    fullness = db.Column(db.Float, nullable=False)

    def __init__(self, id, weight, lat, lon, paper, glass, waste):
        self.id = id
        self.weight = weight
        self.latitude = lat
        self.longitude = lon
        self.paper = paper
        self.glass = glass
        self.waste = waste
        self.fullness = 0
