from sort.models import History
from sort import app

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify

@app.route('/history_info', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = History.serialize_list(History.query.filter_by(id=user_id).all())
    return jsonify(history)