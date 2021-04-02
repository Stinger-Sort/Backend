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
            abort(400)
