from celery.task import task

from ConnectGood.settings import CLIENT_URL_SERVER
from mandrill_script import send_mandrill_email

@task(ignore_result=True)
def notify_event_invitation(event, user, key):
    url = CLIENT_URL_SERVER + '/landing/' + key
    template_vars = [
        {
            'content': user.get_full_name(),
            'name': 'sender'
        },
        {
            'content': event.landing_message,
            'name': 'user_message'
        },
        {
            'content': url,
            'name': 'connect_good_link'
        }
    ]
    receiver = {'email': event.email,
                'name': event.recipient_name,
                'type': 'to'}
    subject = '%s sent you a ConnectGood!' % user.get_full_name()
    template_name = 'ConnectGood Landing Page Link'
    send_mandrill_email(template_vars, receiver, subject, template_name)

@task(ignore_result=True)
def notify_event_accepted_user(event, user):
    template_vars = [
        {
            'content': event.recipient_name,
            'name': 'recipient'
        },
        {
            'content': str(event.donation_amount),
            'name': 'donation_amount'
        }
    ]
    receiver = {'email': user.email,
                'name': user.get_full_name(),
                'type': 'to'}
    subject = 'Awesome! %s accepted your ConnectGood!' % event.recipient_name
    template_name = 'Social Share User'
    send_mandrill_email(template_vars, receiver, subject, template_name)
    return True

@task(ignore_result=True)
def notify_event_accepted_recipient(event, user):
    template_vars = [
        {
            'content': event.recipient_name,
            'name': 'recipient'
        },
        {
            'content': user.company if user.is_corporate_account() else user.get_full_name(),
            'name': 'sender'
        },
        {
            'content': str(event.donation_amount),
            'name': 'donation_amount'
        }
    ]
    receiver = {'email': event.email,
                'name': event.recipient_name,
                'type': 'to'}
    subject = 'Awesome! %s your ConnectGood has been processed!' % event.recipient_name
    template_name = 'Social Share Recipient'
    send_mandrill_email(template_vars, receiver, subject, template_name)
    return True
