from celery.task import task

from users.models import User
from mandrill_script import send_mandrill_email


@task(ignore_result=True)
def post_create_user(user_id):
    user = User.objects.get(pk=user_id)
    template_vars = [{'content': user.first_name, 'name': 'user'}]
    receiver = {'email': user.email,
                'name': user.get_full_name(),
                'type': 'to'}
    subject = 'Welcome to ConnectGood %s!' % user.first_name
    template_name = 'Signup'
    send_mandrill_email(template_vars, receiver, subject, template_name)
    return True
