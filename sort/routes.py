from flask_login import login_user, login_required, logout_user, current_user
from flask import render_template, redirect, url_for, request, abort, jsonify, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from sort import app, db
from sort.models import TrashCan, User


@app.route('/')
def index():
    return 'Ооо повезло-повезло'


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            session.permanent = True
            login_user(user)
            session['user_id'] = user.id
            next_page = request.args.get('next')

            return redirect(next_page)
        else:
            flash('Login or password is not correct')
    else:
        flash('Please fill login and password fields')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')

    if request.method == 'POST':
        if not (login or password or password_confirm):
            flash('Please, fill all fields!')
        elif password != password_confirm:
            flash('Passwords are not equal!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return 'You are logged out'


@app.route('/home', methods=['GET'])
@login_required
def home():
    return current_user.login, {'Content-Type': 'text/html'}


@app.after_request
def redirect_to_signin(response):
    """Перенаправление на страницу авторизации, если пользователь не авторизован"""
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


@app.route('/change_state', methods=['POST'])
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

    increase = trash['paper'] + trash['glass'] + \
        trash['plastic'] + trash['waste']

    if is_exist:
        User.query.filter_by(id=user_id).update(
            {User.score: User.score + increase})
        db.session.commit()
    else:
        abort(404)

    return jsonify({'url': request.url, 'method': request.method,
                    'added_points': increase, 'user_id': user_id})



@app.route('/get_score', methods=['GET'])
@login_required
def get_score():
    """Получение количества баллов пользователя"""
    user_id = session.get('user_id')
    record = User.query.filter_by(id=user_id).first()
    is_exist = record is not None

    if is_exist:
        score = record.score
        return jsonify({'user_id': user_id, 'score': score})
    else:
        abort(404)
