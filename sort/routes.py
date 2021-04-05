from flask import render_template, redirect, url_for, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from sort import app, db
from sort.models import TrashCan, User, Img
from sort.utils import trash_counter, send_email, required_fields, compare_coords
from random import randrange


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
    # TODO: проверка пароля на численный тип
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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Выйти из профиля"""
    return 'You are logged out'


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


@app.route('/change_state', methods=['POST', 'PUT'])
def change_state():
    """Обновление веса мусорки по ее id или создание новой мусорки
    """
    record = request.json
    fields = ('point_id', 'trash')

    required_fields(fields, record)

    id = record['point_id']
    fullness = record['point_full']
    trash = record['trash']

    paper, glass, waste = trash['paper'], trash['glass'], trash['waste']

    weight = trash_counter(trash)
    lat, lon = 0, 0

    is_location = 'location' in record
    if is_location:
        loc = record['location']
        lat, lon = loc['latitude'], loc['longitude']

    can = TrashCan.query.filter_by(id=id)
    is_exist = can.first() is not None

    action_type = 'Update'

    if is_exist:
        update_request = {TrashCan.weight: weight, TrashCan.paper: paper,
                          TrashCan.glass: glass, TrashCan.waste: waste,
                          TrashCan.fullness: fullness}
        if is_location:
            location_update = {TrashCan.latitude: lat, TrashCan.longitude: lon}
            update_request.update(location_update)
        else:
            can.update(update_request)
    else:
        db.session.add(TrashCan(id, weight, lat, lon, paper, glass, waste))
        action_type = 'Creation'

    db.session.commit()
    return jsonify({'host': request.host, 'method': request.method,
                    'charset': request.charset, 'action': action_type,
                    'url': request.url})


@app.route('/trash_cans', methods=['GET'])
def show_trash_cans():
    """Получение информации о заполненности всех существующих мусорных баков"""
    trash_cans = TrashCan.query.order_by(TrashCan.id).all()
    return render_template('trash_cans.html', trash_cans=trash_cans)


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
    fields = ('latitude','longitude')

    # required_fields(fields, req)

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

