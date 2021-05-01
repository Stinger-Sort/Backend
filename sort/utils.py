from flask import abort
from flask_mail import Message
from sort import mail, level_points
import os


def send_email(recipients, html_body):
    """Отправка кода для регистрации пользователя"""

    subject = 'Код для авторизации в приложении Sort'
    sender = 'sort.app.yar@gmail.com'
    text_body = 'Sort'

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


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


def folder_exists(user_id):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def trash_sum(trash_type, history):
    _sum = 0
    for item in history:
        _sum += item[trash_type]

    return _sum
