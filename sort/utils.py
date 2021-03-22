from flask_mail import Message
from sort import app, mail


def trash_counter(trash):
	summ = 0
	for t in trash:
		summ += trash[t]
	return summ


def send_email(subject, recipients, text_body, sender='sort.app.yar@gmail.com', html_body='<h1>ыыы</h1>'):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)