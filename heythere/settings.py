from django.conf import settings as django_settings

BASIC_NOTIFICATIONS = {
    'DEFAULT': {
        'persistant': True,  # stays until dismissed
        'send_onsite': True,  # send as message on site
        'send_email': False,  # send as email
        'headline_template': '{{title}}',  # Django template for headline
        'body_template': '{{body}}'  # Django template for body
    }
}

NOTIFICATIONS = getattr(django_settings, 'NOTIFICATIONS', BASIC_NOTIFICATIONS)
