from __future__ import absolute_import

from django.conf import settings
from django.db import models

from .settings import NOTIFICATIONS
from .utils import render

NOTIFICATION_TYPES = [(key, key.lower().capitalize())
                      for key in NOTIFICATIONS.keys()]


class NotificationManager(models.Manager):
    def create_notification(self, user, notification_type, headline, body):
        notification = self.model(
            user=user, notification_type=notification_type)
        note = NOTIFICATIONS[notification_type]
        notification.headline = render(note['headline_template'], headline)
        notification.body = render(note['body_template'], body)
        notification.save()
        return notification


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
    notification_type = models.CharField(choices=NOTIFICATION_TYPES,
                                         max_length=100)
    headline = models.TextField(blank=True)
    body = models.TextField(blank=True)
    objects = NotificationManager()

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return u'{0.timestamp:%Y/%m/%d %H:%M} - {0.user}'.format(self)
