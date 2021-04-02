from flask import abort
from flask_mail import Message
from sort import mail


def trash_counter(trash: dict):
    """Общий вес мусора"""
    return sum(trash.values())


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
    if fields not in record:
        abort(400)


def db_coords(cans):
    lats_longs = []
    for can in cans:
        lats_longs.append((can.latitude,can.longitude))
    return lats_longs


def compare_coords(cans, lat, lon, precision=0.015):
    close_cans = []
    lats_longs = db_coords(cans)
    for c in lats_longs:
        lat_dif = abs(c[0] - lat)
        long_dif = abs(c[1] - lon)
        if lat_dif < precision and long_dif < precision:
            close_cans.append(c)
    return close_cans