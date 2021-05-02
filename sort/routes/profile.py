from flask import jsonify, abort, redirect, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from werkzeug.utils import secure_filename


from sort import app, db, UPLOAD_FOLDER
from sort.utils import file_ext, folder_exists, trash_sum

from sort.models import User


@app.route('/home', methods=['GET'])
@jwt_required()
def home():
    """Профиль пользователя"""
    user = User.serialize(User.query.filter_by(id=get_jwt_identity()).first())
    return jsonify(user)


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


@app.route('/get_score', methods=['GET'])
@jwt_required()
def get_score():
    """Получение количества баллов пользователя"""
    user_id = get_jwt_identity()
    record = User.query.filter_by(id=user_id).first()

    if not record:
        abort(404)

    return {'user_id': user_id, 'score': record.score}
