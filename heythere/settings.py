from django.conf import settings as django_settings

BASIC_NOTIFICATIONS = {
    'DEFAULT': {
        'persistent': True,  # stays until dismissed
        'send_as_email': False,  # send as email
        'headline_template': '{{headline}}',  # Django template for headline
        'body_template': '{{body}}',  # Django template for body
        'email_field': 'email'  # Assume field named 'email' is user's email
    }
}


def get_notifications():
    return getattr(django_settings, 'NOTIFICATIONS', BASIC_NOTIFICATIONS)

NOTIFICATIONS = get_notifications()
