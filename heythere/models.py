from __future__ import absolute_import

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import models
from django.utils.functional import lazy
from django.utils.timezone import now

from .settings import get_notifications
from .utils import render


def get_notification_types():
    return [(key, key.lower().capitalize())
            for key in get_notifications().keys()]


class NotificationQuerySet(models.query.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def unsent(self):
        return self.filter(sent_at__isnull=True)

    def sent(self):
        return self.filter(sent_at__isnull=False)

    def unread(self):
        return self.filter(active=True)

    def read(self):
        return self.filter(active=False)


class NotificationManager(models.Manager):
    def get_query_set(self):
        return NotificationQuerySet(self.model, using=self._db)

    def create_notification(self, user, notification_type, headline, body):
        notification = self.model(
            user=user, notification_type=notification_type)
        note = get_notifications()[notification_type]
        notification.headline = render(note['headline_template'], headline)
        notification.body = render(note['body_template'], body)
        notification.save()
        return notification

    def for_user(self, user):
        return self.get_query_set().filter(user=user)

    def clear_all(self, user):
        notifications = self.model.objects.select_for_update().for_user(user)
        for notification in notifications:
            notification.read()

    def unread(self, user):
        return self.get_query_set().for_user(user).unread()

    def read(self, user):
        return self.get_query_set().for_user(user).read()

    def unsent(self, user):
        return self.get_query_set().for_user(user).unsent()

    def sent(self, user):
        return self.get_query_set().for_user(user).sent()


class Notification(models.Model):
    """
    Our basic Notification model.

    The `headline` and `body` fields should be filled in
    using the template keys in the chosen notification type.
    """
    timestamp = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL,
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

    def save(self, *args, **kwargs):
        if not self.notification.get('persistant', True) and self.sent_at:
            self.active = False
        return super(Notification, self).save(*args, **kwargs)

    @property
    def notification(self):
        try:
            notification = get_notifications()[self.notification_type]
        except KeyError:
            message = "The notification type {0} doesn't exist.".format(
                self.notification_type)
            raise KeyError(message)
        else:
            return notification

    def read(self):
        self.active = False
        self.save()

    def send(self):
        if self.notification.get('send_email'):
            address = getattr(self.user,
                              self.notification.get('email_field', 'email'))
            send_mail(
                self.headline,
                self.body,
                getattr(django_settings, 'DEFAULT_FROM_EMAIL'),
                [address],
                fail_silently=False
            )
            self.sent_at = now()
            self.save()
