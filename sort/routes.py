from flask import render_template, redirect, url_for, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from sort import app, db, jwt
from sort.models import TrashCan, User
from sort.utils import trash_counter, send_email
from random import randrange


@app.route('/')
def index():
    return 'Ооо повезло-повезло'


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
    return 'You are logged out'


@app.route('/home', methods=['GET'])
@jwt_required()
def home():
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
    if not request.json or not 'id' in request.json:
        abort(400)

    i = request.json['id']
    w = request.json['weight']

    is_exist = TrashCan.query.filter_by(id=i).first() is not None

    action_type = 'Update'

    if is_exist:
        TrashCan.query.filter_by(id=i).update({TrashCan.weight: w})
        db.session.commit()
    else:
        db.session.add(TrashCan(i, w))
        db.session.commit()
        action_type = 'Creation'

    return jsonify({'host': request.host, 'method': request.method,
                    'charset': request.charset, 'action': action_type, 'url': request.url})


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
    is_exist = record is not None

    if is_exist:
        score = record.score
        return jsonify({'user_id': user_id, 'score': score})
    else:
        abort(404)