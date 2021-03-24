from flask_mail import Message
from sort import app, mail

LOGIN_SUBJECT = 'Код для авторизации в приложении Sort'
SENDER = 'sort.app.yar@gmail.com'


def trash_counter(trash):
    """Сумма баллов пользователя"""
    return sum(trash.values())


def send_email(recipients, html_body, text_body=' ', subject=LOGIN_SUBJECT, sender=SENDER):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
