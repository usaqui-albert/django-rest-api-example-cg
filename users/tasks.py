from celery.task import task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from users.models import User
from ConnectGood import settings


@task(ignore_result=True)
def post_create_user(user_id):
    obj = User.objects.get(pk=user_id)
    send_email_to_activate(obj)
    return True

def send_email_to_activate(obj_user):
    subject = 'Welcome to ConnectGood Registration Service'
    from_email = settings.EMAIL_HOST_USER
    to = obj_user.email
    text_content = ''
    htmly = get_template('email_to_active.html')
    d = Context({'complete_name': str(obj_user.first_name) + ' ' + str(obj_user.last_name),
                 'confirm_url': 'www.google.com'
                 })
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
