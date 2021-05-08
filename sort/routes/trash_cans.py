from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity


from sort import app, db
from sort.utils import get_id

from ..models.trash_can import TrashCan


@app.route('/trash_cans', methods=['POST'])
def post_trash_cans():
    """Добавление новой точки сбора"""

    record = request.json
    required_fields(('location'), record)

    loc = record['location']
    lat, lon = loc['latitude'], loc['longitude']
    db.session.add(TrashCan(lat, lon))
    db.session.commit()
    return 'Точка сбора успешно добавлена', 200


@app.route('/trash_cans', methods=['GET'])
def get_trash_cans():
    return jsonify(TrashCan.serialize_list(TrashCan.query.all()))


@app.route('/point_state/<point_id>', methods=['GET'])
def get_point_state(point_id):
    trash_can = TrashCan.query.filter_by(id=point_id).first()
    return f'{trash_can.state}, {trash_can.state_user}'


@app.route('/start_point_session/<point_key>', methods=['PUT'])
@jwt_required()
def start_point_session(point_key):
    """point_key должен быть формата Sort_can_id"""
    record = request.json
    state_user = get_jwt_identity()
    point_id = get_id(point_key)
    trash_can = TrashCan.query.filter_by(id=point_id)

    if trash_can.first().state == 101:
        return ('Мусорка уже в состоянии загрузки', 208)

    trash_can.update({TrashCan.state: 101, TrashCan.state_user: state_user})
    db.session.commit()

    return 'Загрузка мусора началась', 200


@app.route('/end_point_session/<point_key>', methods=['PUT'])
def end_point_session(point_key):
    """point_key должен быть формата Sort_can_id"""
    point_id = get_id(point_key)
    trash_can = TrashCan.query.filter_by(id=point_id)
    trash_can.update({TrashCan.state: 102})
    db.session.commit()

    return 'Загрузка мусора закончилась', 200
