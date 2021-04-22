from flask import redirect, url_for, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from sort import app, db
from sort.models import TrashCan, User, Img, History, Organization, Target
from sort.utils import send_email, required_fields, compare_coords, get_id

from random import randrange
from math import fsum
from datetime import datetime


@app.route('/', methods=['GET'])
def index():
    links = []
    for rule in app.url_map.iter_rules():
        links.append(rule)

    return str(links)


@app.route('/login', methods=['POST'])
def login_page():
    """Email для входа и регистрации"""
    email = request.json['email']
    password = str(randrange(1000, 9999))

    if email:
        user = User.query.filter_by(email=email)
        hash_pwd = generate_password_hash(password)
        if user.first():
            user.update({User.password: hash_pwd})
        else:
            new_user = User(email=email, password=hash_pwd)
            db.session.add(new_user)
        db.session.commit()

        send_email(recipients=[email], html_body=f'<h1>{password}</h1>')
    else:
        abort(400)

    return jsonify({"success": True})


@app.route('/login_with_code', methods=['POST'])
def auth():
    """"Ввод пароля потверждения"""
    email = request.json['email']
    password = request.json['password']

    if email and password and type(password) == int:
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, str(password)):
            access_token = create_access_token(identity=user.id)
            response = jsonify({"msg": "login successful"})
            set_access_cookies(response, access_token)
        else:
            abort(404)
    else:
        abort(400)

    return jsonify({"access_token": access_token})


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


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
    return ('Данные успешно обновлены', 200)


@app.after_request
def redirect_to_signin(response):
    """Перенаправление на страницу авторизации,
        если пользователь не авторизован"""
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


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
    # более точная сумма с помощью fsum
    print(trash)
    weight = fsum(trash.values())

    user = User.query.filter_by(id=user_id)

    db.session.add(History(user_id, trash_can_id, weight, paper, glass, waste))
    trash_can.update({TrashCan.weight: weight})
    user.update({User.score: weight * 10})
    db.session.commit()
    return ('Запись успешно добавлена', 200)


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
    return ('Точка сбора успешно добавлена', 200)


@app.route('/trash_cans', methods=['GET'])
def get_trash_cans():
    trash_cans = TrashCan.serialize_list(TrashCan.query.all())
    return jsonify(trash_cans)


@app.route('/history_info', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = History.serialize_list(History.query.filter_by(id=user_id).all())
    return jsonify(history)


@app.route('/users_info', methods=['GET'])
def get_users_info():
    users = User.serialize_list(User.query.all())
    for u in users:
        u['level'] = User.query.filter_by(id=u['id']).first().level
    return jsonify(users)


@app.route('/organizations_info', methods=['GET'])
def orgs_filter():
    """список организаций с фильтрами по score, name и district"""
    score = request.args.get('score', default=None, type=int)
    name = request.args.get('name', default=None, type=str)
    district = request.args.get('district', default=None, type=str)
    fields = ('name', 'district', 'score')
    filters = {'name': name, 'district': district, 'score': score}
    if 'score' in request.args:
        orgs = Organization.serialize_list(
            Organization.query.order_by(Organization.score).all())
    else:
        for field in fields:
            if filters[field] is None:
                filters.pop(field)
        if any(field in filters for field in fields):
            orgs = Organization.serialize_list(
                Organization.query.filter_by(**filters).all())
        else:
            orgs = Organization.serialize_list(Organization.query.all())
    return jsonify(orgs)


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
    target = Target.serialize(Target.query.filter_by(id=target_id).first())
    return jsonify(target)


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
    return ('Баллы успешно переданы', 200)


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
    trash_can.update({TrashCan.state: 101, TrashCan.state_user: state_user})
    db.session.commit()

    return ('Загрузка мусора началась', 200)


@app.route('/end_point_session/<point_key>', methods=['PUT'])
def end_point_session(point_key):
    """point_key должен быть формата Sort_can_id"""
    point_id = get_id(point_key)
    trash_can = TrashCan.query.filter_by(id=point_id)
    trash_can.update({TrashCan.state: 102})
    db.session.commit()

    return ('Загрузка мусора закончилась', 200)


@app.route('/get_score', methods=['GET'])
@jwt_required()
def get_score():
    """Получение количества баллов пользователя"""
    user_id = get_jwt_identity()
    record = User.query.filter_by(id=user_id).first()

    if not record:
        abort(404)

    score = record.score
    return jsonify({'user_id': user_id, 'score': score})


@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():

    pic = request.files['pic']
    if not pic:
        return 'Изображение отсутствует', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    print(mimetype)
    if not filename or not mimetype:
        return 'Ошибка при загрузке', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    return 'Изображение загружено!', 200


@app.route('/close_cans', methods=['POST'])
def get_close_cans():
    req = request.json
    fields = ('latitude', 'longitude')

    required_fields(fields, req)

    lat = req['latitude']
    lon = req['longitude']
    trash_cans = TrashCan.query.order_by(TrashCan.id).all()

    precison = 0.015
    if 'precison' in req:
        precison = req['precison']

    close_cans = compare_coords(trash_cans, lat, lon, precison)
    json = {'close_cans': len(close_cans)}

    n = 1
    for c in close_cans:
        json['latitude_' + str(n)] = c[0]
        json['longitude_' + str(n)] = c[1]
        n += 1

    return jsonify(json)


@app.route('/add_org', methods=['POST'])
def add_org():
    req = request.json
    fields = ('name', 'district')

    required_fields(fields, req)

    n, d = req['name'], req['district']
    db.session.add(Organization(name=n, district=d))
    db.session.commit()

    return 'Организация добавлена', 200
