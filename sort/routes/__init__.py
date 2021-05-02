from flask import redirect, url_for, request, abort, jsonify, send_file
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt_identity

from werkzeug.utils import secure_filename

from sort import app, db, UPLOAD_FOLDER
from sort.models import TrashCan, User, History, Organization, Target
from sort.utils import send_email_confirm, required_fields, compare_coords, get_id
from sort.utils import trash_sum, folder_exists, folder_exists, file_ext

from math import fsum


@app.route('/', methods=['GET'])
def index():
    return 'Sort API v. 0.1'


@app.route('/home', methods=['GET'])
@jwt_required()
def home():
    """Профиль пользователя"""
    user = User.serialize(User.query.filter_by(id=get_jwt_identity()).first())
    return jsonify(user)


@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Обновить данные профиля"""
    record = request.json

    query_dict = {
        User.first_name: 'first_name', User.last_name: 'last_name',
        User.city: 'city', User.phone_number: 'phone_number'
    }

    # создаём словарь с нужными полями, находим значение в запросе по ключу
    upd_dict = {x[0]: record[x[1]]
                for x in query_dict.items() if x[1] in record.keys()}

    user_query = User.query.filter_by(id=get_jwt_identity())
    user_query.update(upd_dict)
    db.session.commit()
    return 'Данные успешно обновлены', 200


@app.route('/change_state', methods=['POST'])
def change_state():
    """Создание записи с видом и весом мусора"""
    record = request.json
    fields = ('trash_can_id', 'trash')
    required_fields(fields, record)

    trash_can_id = record['trash_can_id']
    user_id = record['user_id']
    fullness = record['trash_can_full']
    trash = record['trash']

    paper, glass, waste = trash['paper'], trash['glass'], trash['waste']

    trash_can = TrashCan.query.filter_by(id=trash_can_id)
    cur_trash_can = trash_can.first()

    trash.update({"prev_value": cur_trash_can.weight})

    weight = fsum(trash.values())

    user = User.query.filter_by(id=user_id)

    db.session.add(History(user_id, trash_can_id, weight, paper, glass, waste))
    trash_can.update({TrashCan.weight: weight})
    user.update({User.score: weight * 10})
    db.session.commit()
    return 'Запись успешно добавлена', 200


@app.route('/trash_cans', methods=['POST'])
def post_trash_cans():
    """Добавление новой точки сбора"""
    fields = ('location')
    record = request.json
    # required_fields(fields, record)

    loc = record['location']
    lat, lon = loc['latitude'], loc['longitude']
    db.session.add(TrashCan(lat, lon))
    db.session.commit()
    return 'Точка сбора успешно добавлена', 200


@app.route('/trash_cans', methods=['GET'])
def get_trash_cans():
    return jsonify(TrashCan.serialize_list(TrashCan.query.all()))


@app.route('/users_info', methods=['GET'])
def get_users_info():
    users = User.serialize_list(User.query.all())
    for u in users:
        u['level'] = User.query.filter_by(id=u['id']).first().level
    return users


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


@app.route('/targets_info', methods=['GET'])
def get_targets_info():
    record = db.session.query(Target, Organization).join(
        Target, Organization.id == Target.organization_id).all()

    query = []
    for rec in record:
        org = rec.Organization
        target = rec.Target
        query.append({'organization_name': org.name, 'id': target.id,
                      'total_score': target.total_score, 'name': target.name,
                      'score': target.score})
    return jsonify(query)


@app.route('/targets_info/<target_id>', methods=['GET'])
def get_one_target(target_id):
    return Target.serialize(Target.query.filter_by(id=target_id).first())


@app.route('/targets_info/<target_id>', methods=['PUT'])
@jwt_required()
def post_one_target(target_id):
    transfer_points = int(request.json['transfer_points'])

    user_query = User.query.filter_by(id=get_jwt_identity())
    user = user_query.first()

    if user.score < transfer_points:
        return (f'Недостаточно баллов, у вас: {user.score}, необходимо {transfer_points}', 400)

    if user.score <= 0:
        return ('Баллы должны быть больше нуля', 400)

    user_query.update({User.score: user.score - transfer_points})

    target_query = Target.query.filter_by(id=target_id)
    target = target_query.first()

    target_query.update({Target.score: fsum((target.score, transfer_points))})
    db.session.commit()
    return 'Баллы успешно переданы', 200


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


@app.route('/get_score', methods=['GET'])
@jwt_required()
def get_score():
    """Получение количества баллов пользователя"""
    user_id = get_jwt_identity()
    record = User.query.filter_by(id=user_id).first()

    if not record:
        abort(404)

    score = record.score
    return {'user_id': user_id, 'score': score}



@app.route('/upload_profile_pic', methods=['GET', 'POST'])
@jwt_required()
def upload_profile_pic():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # folder_path = folder_exists(get_jwt_identity())
            file.save(os.path.join(UPLOAD_FOLDER,
                      'profile_pic' + file_ext(filename)))

            return redirect(url_for('upload_profile_pic',
                                    filename=filename))
    return 'success', 200


@app.route('/profile_pic')
# @jwt_required()
def get_profile_pic():
    # folder_exists(get_jwt_identity())
    return send_file(UPLOAD_FOLDER + '/profile_pic.jpg')


@app.route('/user_analytics', methods=['GET'])
# @jwt_required()
def get_user_analytics():

    history = History.serialize_list(
        History.query.filter_by(user_id=1).all())

    trash_types = ('paper', 'glass', 'waste', 'weight')

    return trash_sum(trash_types, history)