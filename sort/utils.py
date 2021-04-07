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
    for field in fields:
        if field not in record.keys():
            abort(400, f'Нет необходимого поля: {field}')


def cans_info(cans: list):
    """Вывод информации о точках сборах в json"""
    info = []
    for can in cans:
        info.append({"id": can.id, "weight": can.weight,
                     "fullness": can.fullness, "latitude": can.latitude,
                     "longitude": can.longitude})
    return info


def history_info(users: list):
    """Вывод информации о точках сборах в json"""
    info = []
    for his in history:
        info.append({"id": his.id, "weight": his.weight,
                     "user_id": his.user_id, "trash_can_id": his.trash_can_id,
                     "fullness": his.fullness, "paper": his.paper,
                     "glass": his.glass, "waste": his.waste})
    return info


def users_info(users: list):
    """Вывод информации о точках сборах в json"""
    info = []
    for user in users:
        info.append({"id": user.id, "email": user.id,
                     "score": user.score})
    return info


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
