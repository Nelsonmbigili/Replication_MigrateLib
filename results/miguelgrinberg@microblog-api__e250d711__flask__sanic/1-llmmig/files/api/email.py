from threading import Thread

from sanic import Sanic
from sanic_ext import Extend
from sanic_mail import Mail, Message

from api.app import mail


def send_async_email(app, to, subject, template, **kwargs):
    async with app.ext.get_context():  # Sanic's equivalent of app context
        msg = Message(
            subject=subject,
            recipients=[to],
            body=app.ext.jinja.render(template + '.txt', **kwargs),
            html=app.ext.jinja.render(template + '.html', **kwargs)
        )
        await mail.send(msg)


def send_email(to, subject, template, **kwargs):  # pragma: no cover
    app = Sanic.get_app()  # Get the current Sanic app instance
    thread = Thread(target=send_async_email, args=(app, to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
