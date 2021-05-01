from sort.models import User
from sort import app

from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify

from random import randrange

@app.route('/registration', methods=['POST'])
def registration_page():
    record = request.json
    fields = ('email', 'password', 'first_name')

    email = record['email']
    password = record['password']
    first_name = record['first_name']

    required_fields(fields, record)

    user = User.query.filter_by(email=email).first()

    if user:
        return 'Пользователь с таким email уже зарегистрирован', 409
    else:
        hash_pwd = generate_password_hash(password)

        email_confirm = str(randrange(1000, 9999))
        hash_email_confirm = generate_password_hash(email_confirm)

        new_user = User(email=email, password=hash_pwd,
                        first_name=first_name, email_confirm=hash_email_confirm)

        db.session.add(new_user)
        db.session.commit()

        send_email(recipients=[email],
                   html_body=f'<h1>{email_confirm}</h1>')

    return jsonify({"success": True})


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

    return jsonify({"access_token": access_token})


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

    return jsonify({"access_token": access_token})
    


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    unset_jwt_cookies(response)
    return jsonify({"msg": "logout successful"})