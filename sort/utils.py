from flask import abort, current_app
from flask_mail import Message
from sort import mail, level_points, app
from math import fsum

from threading import Thread


def thread_send_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipients, html_body):
    """Отправка кода для регистрации пользователя"""

    SUBJECT = 'Код для авторизации в приложении Sort'
    TEXT_BODY = 'Sort'

    msg = Message(
        SUBJECT, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=recipients)
    msg.body = TEXT_BODY
    msg.html = html_body
    thr = Thread(target=thread_send_email, args=[
                 current_app._get_current_object(), msg])
    thr.start()
    return thr


def required_fields(fields: tuple, record: dict):
    """Проверка запроса на необходимые поля"""
    for field in fields:
        if field not in record.keys():
            abort(400, f'Нет необходимого поля: {field}')


def db_coords(cans: list):
    lats_longs = []
    for can in cans:
        lats_longs.append((can.latitude, can.longitude))
    return lats_longs


def compare_coords(cans: list, lat: float, lon: float, precision=0.015):
    close_cans = []
    lats_longs = db_coords(cans)
    for c in lats_longs:
        lat_dif = abs(c[0] - lat)
        long_dif = abs(c[1] - lon)
        if lat_dif < precision and long_dif < precision:
            close_cans.append(c)
    return close_cans


def get_id(key):
    return int(key.replace("Sort_can_", ""))


def level_counter(score: int):
    level = 0
    for l in level_points.keys():
        if score >= level_points[l] and level < int(l):
            level = int(l)
    return level
