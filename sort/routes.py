from flask import render_template, redirect, url_for, request, abort, jsonify

from sort import app, db
from sort.models import Message, TrashCan

@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')


@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html', messages=Message.query.all())


@app.route('/add_message', methods=['POST'])
def add_message():
    text = request.form['text']
    tag = request.form['tag']

    db.session.add(Message(text, tag))
    db.session.commit()

    return redirect(url_for('main'))


@app.route('/change_state', methods=['POST'])
def change_state():
    if not request.json or not 'id' in request.json:
        abort(400)

    i = request.json['id']
    w = request.json['weight']

    is_exist = False

    action_type = 'Update'

    try:
        TrashCan.query.filter_by(id = i).one()
        is_exist = True
    except:
        is_exist = False

    if is_exist:
        TrashCan.query.filter_by(id = i).update({TrashCan.weight: w})
        db.session.commit()
    else:
        db.session.add(TrashCan(i, w))        
        db.session.commit()
        action_type = 'Creation'

    return jsonify({'host': request.host,'method': request.method,         
        'charset': request.charset,'action': action_type, 'url': request.url})


@app.route('/trash_cans', methods=['GET'])
def show_trash_cans():
    trash_cans = TrashCan.query.order_by(TrashCan.id).all()
    return render_template('trash_cans.html', trash_cans = trash_cans)