from threading import Thread
from bottle import template

# Assuming you have a mail sending function defined elsewhere
# from your_mail_library import send_mail

def send_async_email(to, subject, template_name, **kwargs):
    # Construct the email body and HTML content
    body = template(template_name + '.txt', **kwargs)
    html = template(template_name + '.html', **kwargs)
    
    # Send the email using your mail sending function
    # send_mail(to, subject, body, html)

def send_email(to, subject, template_name, **kwargs):  # pragma: no cover
    thread = Thread(target=send_async_email, args=(to, subject, template_name),
                    kwargs=kwargs)
    thread.start()
    return thread
