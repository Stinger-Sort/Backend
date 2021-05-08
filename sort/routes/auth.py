from sort.models import User
from sort.utils import required_fields, send_email_confirm, send_password_reset
from sort import app, db

from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, abort

from random import randrange


@app.route('/registration', methods=['POST'])
def registration_page():
    record = request.json
    fields = ('email', 'password', 'name')

    email = record['email']
    password = record['password']

    required_fields(fields, record)

    user = User.query.filter_by(email=email).first()

    if user:
        return 'Пользователь с таким email уже зарегистрирован', 409
    else:
        hash_pwd = generate_password_hash(password)

        confirm_code = str(randrange(1000, 9999))
        hash_confirm_code = generate_password_hash(confirm_code)

        new_user = User(email=email, password=hash_pwd,
                        name=record['name'], email_confirm=hash_confirm_code,
                        phone_number=record['phone_number'])

        db.session.add(new_user)
        db.session.commit()

        send_email_confirm(recipient=email, confirm_code=confirm_code)

    return {"success": True}


@app.route('/email_confirm', methods=['POST'])
def email_confirm_page():
    """"Ввод пароля потверждения"""

    record = request.json

    email = record['email']
    password = record['password']

    if email and password and type(password) == int:
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.email_confirm, str(password)):
            access_token = create_access_token(identity=user.id)
            response = jsonify({"msg": "login successful"})
            set_access_cookies(response, access_token)
        else:
            abort(400)
    else:
        abort(400)

    return {"access_token": access_token}


@app.route('/login', methods=['POST'])
def login_page():
    record = request.json

    email = record['email']
    password = record['password']

    if email and password:
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            response = jsonify({"msg": "login successful"})
            set_access_cookies(response, access_token)
        else:
            abort(400)
    else:
        abort(400)

    return {"access_token": access_token}

@app.route("/password_reset", methods=["POST"])
def page_password_reset():
    email = request.json['email']
    user = User.query.filter_by(email=email)

    if not user.first():
        return 'Пользователь с таким email не существует', 400
      
    temp_password = str(randrange(1000, 9999))
    hash_temp_password = generate_password_hash(temp_password)

    user.update({User.password: hash_temp_password})

    send_password_reset(recipient=email, confirm_code=temp_password)

    db.session.commit()
    return 'Временный пароль выслан на почту', 200


@app.route("/change_password", methods=["POST"])
def page_change_password():
    record = request.json

    email = record['email']
    old_password = record['old_password']
    new_password = record['new_password']

    user_query = User.query.filter_by(email=email)
    user = user_query.first()

    if not user:
        return 'Неверный email', 400
    if not check_password_hash(user.password, old_password):
        return 'Пароли не совпадают', 400

    hash_new_password = generate_password_hash(new_password)
    user_query.update({User.password: hash_new_password})
    
    db.session.commit()
    return 'Пароль успешно изменён', 200


@app.route("/logout", methods=["POST"])
@jwt_required()
def page_logout():
    unset_jwt_cookies(response)
    return {"msg": "logout successful"}
