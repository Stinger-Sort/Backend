from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity


from sort import app, db
from sort.models import Target, Organization, User

from math import fsum

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
    return Target.serialize(Target.query.filter_by(id=target_id).first())


@app.route('/targets_info/<target_id>', methods=['PUT'])
@jwt_required()
def post_one_target(target_id):
    transfer_points = int(request.json['transfer_points'])

    user_query = User.query.filter_by(id=get_jwt_identity())
    user = user_query.first()

    if user.score < transfer_points:
        return f'Недостаточно баллов, у вас: {user.score}, необходимо {transfer_points}', 400

    if transfer_points <= 0:
        return 'Баллы должны быть больше нуля', 400

    user_query.update({User.score: user.score - transfer_points, 
                       User.donations_number: user.donations_number + 1})

    target_query = Target.query.filter_by(id=target_id)
    target = target_query.first()

    target_query.update({Target.score: fsum((target.score, transfer_points))})
    db.session.commit()
    return 'Баллы успешно переданы', 200