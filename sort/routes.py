from flask import redirect, url_for, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from sort import app, db
from sort.models import TrashCan, User, Img, History
from sort.utils import total_weight, send_email, required_fields, history_info
from sort.utils import compare_coords, cans_info, users_info
from random import randrange
from math import fsum


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
            access_token = create_access_token(identity=email)
        else:
            abort(404)
    else:
        abort(400)

    return jsonify({"access_token": access_token})


@app.route('/logout', methods=['GET'])
@jwt_required()
def logout_route():
    """Выйти из профиля"""
    return "logout()"


@app.route('/home', methods=['GET'])
@jwt_required()
def home():
    """Профиль пользователя"""
    current_user = get_jwt_identity()
    return jsonify({"Current user": current_user})


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

    trash.update({"prev_value", TrashCan.weight})
    # более точная сумма с помощью fsum
    weight = fsum(trash.values())

    trash_can = TrashCan.query.filter_by(id=trash_can_id)
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
    trash_cans = cans_info(TrashCan.query.order_by(TrashCan.id).all())
    return jsonify(trash_cans)


@app.route('/history_info', methods=['GET'])
def get_history():
    history = history_info(History.query.order_by(History.id).all())
    return jsonify(history)


@app.route('/users_info', methods=['GET'])
def get_users_info():
    users = users_info(User.query.order_by(User.id).all())
    return jsonify(users)


@app.route('/point_state/<point_id>', methods=['GET'])
def get_point_state(point_id):
    trash_can = TrashCan.query.filter_by(id=point_id).first()
    return f'{trash_can.state}, {trash_can.state_user}'


@app.route('/start_point_session/<point_id>', methods=['PUT'])
def start_point_session(point_id):
    record = request.json
    state_user = record['state_user']
    trash_can = TrashCan.query.filter_by(id=point_id)
    trash_can.update({TrashCan.state: 101, TrashCan.state_user: state_user})
    db.session.commit()

    return ('Загрузка мусора началась', 200)


@app.route('/end_point_session/<point_id>', methods=['PUT'])
def end_point_session(point_id):
    trash_can = TrashCan.query.filter_by(id=point_id).first()
    trash_can.update({TrashCan.state: 102})
    db.session.commit()

    return ('Загрузка мусора закончилась', 200)


@app.route('/add_points', methods=['POST'])
def add_points():
    """Увеличение количества баллов пользователя"""

    record = request.json
    fields = ('user_id')
    required_fields(fields, record)

    user_id = record['user_id']
    trash = record['trash']

    is_exist = User.query.filter_by(
        id=user_id).first() is not None

    increase = trash_counter(trash)

    if is_exist:
        User.query.filter_by(id=user_id).update(
            {User.score: User.score + increase})
        db.session.commit()
    else:
        abort(404)

    return jsonify({'url': request.url, 'method': request.method,
                    'added_points': increase, 'user_id': user_id})


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
