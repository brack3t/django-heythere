from django.conf import settings as django_settings

BASIC_NOTIFICATIONS = {
    'DEFAULT': {
        'persistant': True,  # stays until dismissed
        'send_onsite': True,  # send as message on site
        'send_email': False,  # send as email
        'headline_template': '{{headline}}',  # Django template for headline
        'body_template': '{{body}}',  # Django template for body
        'email_field': 'email'
    }
}

# NOTIFICATIONS = getattr(
#    django_settings, 'NOTIFICATIONS', BASIC_NOTIFICATIONS)


def get_notifications():
    return getattr(django_settings, 'NOTIFICATIONS', BASIC_NOTIFICATIONS)

NOTIFICATIONS = get_notifications()
