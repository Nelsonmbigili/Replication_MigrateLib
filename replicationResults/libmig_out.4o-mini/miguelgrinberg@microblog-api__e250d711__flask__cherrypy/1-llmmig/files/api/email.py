from threading import Thread

import cherrypy

# Assuming a similar mail sending function is available in the CherryPy context
from api.app import mail


def send_async_email(to, subject, template, **kwargs):
    # Directly using the mail object without app context
    msg = mail.Message(subject, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


def send_email(to, subject, template, **kwargs):  # pragma: no cover
    thread = Thread(target=send_async_email, args=(to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
