from flask_mail import Message
from sort import app, mail

login_subject = 'Код для авторизации в приложении Sort'
sender='sort.app.yar@gmail.com'


def trash_counter(trash):
	summ = 0
	for t in trash:
		summ += trash[t]
	return summ


def send_email(recipients, html_body, text_body=' ',subject=login_subject, sender=sender):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)