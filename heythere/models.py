from __future__ import absolute_import

import ast

from django.conf import settings as django_settings
from django.core.mail import send_mail, send_mass_mail
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
            user=user,
            notification_type=notification_type,
            headline_dict=headline,
            body_dict=body
        )
        notification.save()
        return notification

    def for_user(self, user):
        return self.get_query_set().filter(user=user)

    def clear_all(self, user):
        notifications = self.model.objects.select_for_update().for_user(user)
        for notification in notifications:
            notification.read()

    def send_all_unsent(self, fail_silently=False):
        notifications = self.model.objects.all_unsent()
        emails = [note.mail_tuple for note in
                  notifications if note.send_as_email]
        send_mass_mail(emails, fail_silently=fail_silently)

        for note in notifications:
            note.sent_at = now()
            note.save()

    def all_unsent(self):
        return self.get_query_set().unsent()

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
    notification_type = models.CharField(max_length=100, default=u'DEFAULT')
    headline_dict = models.TextField(blank=True)
    body_dict = models.TextField(blank=True)
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
        if not hasattr(self.headline_dict, 'keys'):
            headline_dict = ast.literal_eval(self.headline_dict)
            body_dict = ast.literal_eval(self.body_dict)
        else:
            headline_dict = self.headline_dict
            body_dict = self.body_dict

        self.headline = render(
            self.notification_dict['headline_template'],
            headline_dict
        )
        self.body = render(
            self.notification_dict['body_template'],
            body_dict
        )
        if not self.persistent and self.sent_at:
            self.active = False
        super(Notification, self).save(*args, **kwargs)

    @property
    def notification_dict(self):
        try:
            notification = get_notifications()[self.notification_type]
        except KeyError:
            message = u"The notification type {0} doesn't exist.".format(
                self.notification_type)
            raise KeyError(message)
        else:
            return notification

    @property
    def mail_tuple(self):
        return (self.headline, self.body,
                getattr(django_settings, u'DEFAULT_FROM_EMAIL'),
                [getattr(self.user,
                         getattr(self.notification_dict, u'email_field',
                                 u'email'))],
                )

    @property
    def persistent(self):
        return self.notification_dict.get(u'persistent', True)

    @property
    def send_as_email(self):
        return self.notification_dict.get(u'send_as_email', False)

    def read(self):
        self.active = False
        self.save()

    def send_email(self, fail_silently=False):
        if self.send_as_email:
            send_mail(*self.mail_tuple, fail_silently=fail_silently)
            self.sent_at = now()
            self.save()
