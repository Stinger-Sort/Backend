class Serializer(object):

    def serialize(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
