from celery.task import task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from ConnectGood.settings import EMAIL_HOST_USER, CLIENT_URL_SERVER


@task(ignore_result=True)
def notify_event_invitation(event, user, key):
    subject = 'ConnectGood Event Created Service'
    url = CLIENT_URL_SERVER + '/landing/' + key
    htmly = get_template('email_event_created.html')
    context = Context({'recipient_name': event.recipient_name,
                       'username': user.first_name,
                       'url': url})
    sending_email(htmly.render(context), subject, event.email)

@task(ignore_result=True)
def notify_event_accepted(event, user):
    subject = 'Your ConnectGood Has Been Accepted'
    htmly = get_template('email_event_accepted.html')
    context = Context({'recipient_name': event.recipient_name,
                       'username': user.first_name})
    sending_email(htmly.render(context), subject, user.email)

@task(ignore_result=True)
def notify_event_rejected(event, user):
    subject = 'Your ConnectGood Has Been Rejected'
    htmly = get_template('email_event_rejected.html')
    context = Context({'recipient_name': event.recipient_name,
                       'username': user.first_name})
    sending_email(htmly.render(context), subject, user.email)

def sending_email(html_content, subject, receiver):
    msg = EmailMultiAlternatives(subject, '', EMAIL_HOST_USER, [receiver])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
