import mandrill
from ConnectGood.settings import MANDRILL_API_KEY, MANDRILL_SENDER_EMAIL

def send_mandrill_email(template_vars, to, subject, template_name):
    try:
        mandrill_client = mandrill.Mandrill(MANDRILL_API_KEY)
        template_content = []
        message = {
            'from_email': MANDRILL_SENDER_EMAIL,
            'from_name': 'ConnectGood',
            'global_merge_vars': template_vars,
            'subject': subject,
            'to': [to],
            'important': True,
            'track_clicks': None,
            'track_opens': None,
            'url_strip_qs': None,
        }
        result = mandrill_client.messages.send_template(template_name=template_name,
                                                        template_content=template_content,
                                                        message=message,
                                                        async=False)
    except mandrill.Error as err:
        return 'A mandrill error occurred: %s - %s' % (err.__class__, err)
    else:
        return 'The email was %s' % result[0]['status']
