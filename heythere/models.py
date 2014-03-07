from __future__ import absolute_import

from django.conf import settings
from django.db import models
from django.utils.functional import lazy

# from .settings import NOTIFICATIONS
from .utils import render

# NOTIFICATION_TYPES = [(key, key.lower().capitalize())
#                       for key in NOTIFICATIONS.keys()]


def get_notification_types():
    from .settings import get_notifications
    return [(key, key.lower().capitalize()) for key in get_notifications().keys()]


class NotificationManager(models.Manager):
    def create_notification(self, user, notification_type, headline, body):
        from .settings import NOTIFICATIONS
        notification = self.model(
            user=user, notification_type=notification_type)
        note = NOTIFICATIONS[notification_type]
        notification.headline = render(note['headline_template'], headline)
        notification.body = render(note['body_template'], body)
        notification.save()
        return notification

    def clear_all(self, user):
        notifications = self.model.objects.select_for_update().filter(
            user=user)
        for notification in notifications:
            notification.read()

    def unread(self, user):
        return self.model.objects.filter(user=user, active=True)


class Notification(models.Model):
    """
    Our basic Notification model.

    The `headline` and `body` fields should be filled in
    using the template keys in the chosen notification type.
    """
    timestamp = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='notifications')
    notification_type = models.CharField(max_length=100)
    headline = models.TextField(blank=True)
    body = models.TextField(blank=True)
    objects = NotificationManager()

    def __init__(self, *args, **kwargs):
        super(Notification, self).__init__(*args, **kwargs)
        self._meta.get_field_by_name('notification_type')[0]._choices = lazy(
            get_notification_types, list)()

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return u'{0.timestamp:%Y/%m/%d %H:%M} - {0.user}'.format(self)

    def read(self):
        self.active = False
        self.save()
