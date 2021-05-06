from flask import abort
from flask_mail import Message
from sort import mail, level_points, ALLOWED_EXTENSIONS
from typing import List
import os


def send_email_confirm(recipient: str, confirm_code: str) -> None:
    """Отправка кода для регистрации пользователя"""

    subject = 'Код для авторизации в приложении Sort'
    sender = 'sort.app.yar@gmail.com'
    text_body = 'Sort'

    msg = Message(subject, sender=sender, recipients=[recipient])
    msg.body = text_body
    msg.html = f'<h1>{confirm_code}</h1>'
    mail.send(msg)


def required_fields(fields: tuple, record: dict) -> None:
    """Проверка запроса на необходимые поля"""
    for field in fields:
        if field not in record.keys():
            abort(400, f'Нет необходимого поля: {field}')


def db_coords(cans: list) -> List[tuple]:
    lats_longs = []
    for can in cans:
        lats_longs.append((can.latitude, can.longitude))
    return lats_longs


def compare_coords(cans: list, lat: float, lon: float, precision=0.015) -> list:
    close_cans = []
    lats_longs = db_coords(cans)
    for c in lats_longs:
        lat_dif = abs(c[0] - lat)
        long_dif = abs(c[1] - lon)
        if lat_dif < precision and long_dif < precision:
            close_cans.append(c)
    return close_cans


def get_id(key: str) -> int:
    return int(key.replace("Sort_can_", ""))


def level_counter(score: int) -> int:
    level = 0
    for l in level_points.keys():
        if score >= level_points[l] and level < int(l):
            level = int(l)
    return level


def folder_exists(user_id: int) -> str:
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def trash_sum(trash_types: tuple, history: List[str]) -> dict:
    trash = dict.fromkeys(trash_types, 0)

    for trash_type in trash_types:
        for item in history:
            trash[trash_type] += item[trash_type]

    return trash


def file_ext(filename: str) -> str:
    return '.' + filename.rpartition('.')[2]


def allowed_file(filename: str) -> str:
    return file_ext(filename) in ALLOWED_EXTENSIONS