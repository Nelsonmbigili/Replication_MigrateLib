from threading import Thread

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from flask_mail import Message

from api.app import mail

# Initialize FastAPI app and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Assuming templates are in a 'templates' directory

def send_async_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.body = templates.get_template(template + '.txt').render(**kwargs)  # Using Jinja2 to render
    msg.html = templates.get_template(template + '.html').render(**kwargs)  # Using Jinja2 to render
    mail.send(msg)

def send_email(to, subject, template, **kwargs):  # pragma: no cover
    thread = Thread(target=send_async_email, args=(to, subject, template),
                    kwargs=kwargs)
    thread.start()
    return thread
