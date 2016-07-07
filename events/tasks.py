from celery.task import task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from ConnectGood import settings


@task(ignore_result=True)
def send_email_to_notify(event, user):
    subject = 'ConnectGood Event Created Service'
    from_email = settings.EMAIL_HOST_USER
    to = event.email
    text_content = ''
    htmly = get_template('email_event_created.html')
    d = Context({'recipient_name': event.recipient_name,
                 'username': user.first_name
        })
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
