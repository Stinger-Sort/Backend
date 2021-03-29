from flask import render_template, redirect, url_for, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from sort import app, db, jwt
from sort.models import TrashCan, User
from sort.utils import trash_counter, send_email
from random import randrange


@app.route('/login', methods=['POST'])
def login_page():
    """Email для входа и регистрации"""
    email = request.json['email']
    password = str(randrange(1000, 9999))
    success = False

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
        success = True
    else:
        abort(400)

    return jsonify({"success": success})


@app.route('/login_with_code', methods=['POST'])
def auth():
    """"Ввод пароля потверждения"""
    email = request.json['email']
    password = str(request.json['password'])

    if email and password:
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
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
    """Перенаправление на страницу авторизации, если пользователь не авторизован"""
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


@app.route('/change_state', methods=['POST', 'PUT'])
def change_state():
    """Обновление веса мусорки по ее id или создание новой мусорки"""
    """форматы для json: 
        {'id': 1, 'weight':2.3}
        или
        {'id': 1, 'weight':2.3, 'location': {'latitude':54.97, 'longtitude':73.38}}
    """
    if not request.json or not 'id' in request.json or not 'weight' in request.json:
        abort(400)

    id = request.json['id']
    weight = request.json['weight']
    lat, lon = 0, 0
    if 'location' in request.json:
        loc = request.json['location']
        lat, lon = loc['latitude'], loc['longtitude']

    can = TrashCan.query.filter_by(id=id)   
    is_exist = can.first() is not None

    action_type = 'Update'

    if is_exist:
        can.update({TrashCan.weight: weight})
        if 'location' in request.json:
            can.update({TrashCan.latitude:lat,TrashCan.longtitude:lon})
    else:
        db.session.add(TrashCan(id, weight, lat, lon))
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

    user_id = request.json['user_id']

    if not request.json or not user_id:
        abort(400)

    trash = request.json['trash']

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