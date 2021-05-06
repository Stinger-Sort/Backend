from flask import request, jsonify

from sort import app, db
from sort.models import User, History, Organization
from sort.utils import required_fields


from ..models.trash_can import TrashCan

from math import fsum


@app.route('/', methods=['GET'])
def index():
    return 'Sort API v. 0.1'


@app.route('/change_state', methods=['POST'])
def change_state():
    """Создание записи с видом и весом мусора"""
    record = request.json
    fields = ('trash_can_id', 'trash')
    required_fields(fields, record)

    trash_can_id = record['trash_can_id']
    user_id = record['user_id']
    trash = record['trash']
    full = record['full']

    trash_can = TrashCan.query.filter_by(id=trash_can_id)
    cur_trash_can = trash_can.first()

    if not cur_trash_can:
        return 'Точка сбора не существует', 400

    trash.update({"prev_value": cur_trash_can.weight})

    weight = fsum(trash.values())

    user = User.query.filter_by(id=user_id)

    db.session.add(History(user_id, trash_can_id, weight,
                           trash['paper'], trash['glass'],
                           trash['waste'], trash['plastic']))

    trash_can.update({TrashCan.full_paper: full['paper'],
                      TrashCan.full_glass: full['glass'],
                      TrashCan.full_waste: full['waste'],
                      TrashCan.full_plastic: full['plastic']})
    user.update({User.score: weight * 10})
    db.session.commit()
    return 'Запись успешно добавлена', 200


@app.route('/users_info', methods=['GET'])
def get_users_info():
    order = request.args.get('order', default=None,type=str)

    if order == "down_to_up":
        users = User.query.order_by(User.score).all()
    else:
        users = User.query.order_by(User.score.desc()).all()

    users = User.serialize_list(users)
    for u in users:
        u['level'] = User.query.filter_by(id=u['id']).first().level
    return jsonify(users)


@app.route('/users_search', methods=['GET'])
def users_search():
    query = request.args.get('query', default=None, type=str)
    users = User.query.filter(User.first_name.like('%'+query+'%')).all()
    users = User.serialize_list(users)
    for u in users:
        u['level'] = User.query.filter_by(id=u['id']).first().level
    return jsonify(users)


@app.route('/organizations_info', methods=['GET'])
def orgs_filter():
    """список организаций с фильтрами по score, name и district"""
    name = request.args.get('name', default=None, type=str)
    district = request.args.get('district', default=None, type=str)
    fields = ('name', 'district')
    filters = {'name': name, 'district': district}

    for field in fields:
        if filters[field] is None:
            filters.pop(field)
    if any(field in filters for field in fields):
        orgs = Organization.query.filter_by(**filters)
    else:
        orgs = Organization.query

    if 'score' in request.args:
        orgs = orgs.order_by(Organization.score.desc())

    result = Organization.serialize_list(orgs.all())
    return jsonify(result)


@app.route('/orgs_search', methods=['GET'])
def orgs_search():
    query = request.args.get('query', default=None, type=str)
    orgs = Organization.query.filter(Organization.name.like('%'+query+'%')).all()
    orgs = Organization.serialize_list(orgs)
    return jsonify(orgs)