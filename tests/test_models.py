from __future__ import absolute_import

import pytest

from django import test
from django.contrib.auth.models import User
from django.core import mail
from django.test.utils import override_settings

from heythere.models import Notification


class TestNotificationModel(test.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser',
                                             email='test@example.com')
        self.headline = 'This is a notification'

    def _create_notification(self, notification_type='DEFAULT'):
        notification = Notification.objects.create_notification(
            user=self.user,
            notification_type=notification_type,
            headline={'headline': self.headline},
            body={'body': 'This is the body'}
        )
        return notification

    def test_basic_notification(self):
        notification = self._create_notification()

        self.assertTrue(notification.active)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.headline, self.headline)

    def test_all_of_a_users_notifications(self):
        self._create_notification()
        self._create_notification()
        self._create_notification()

        self.assertEqual(Notification.objects.for_user(self.user).count(), 3)

    def test_reading_notification(self):
        notification = self._create_notification()
        self.assertTrue(notification.active)
        notification.read()
        self.assertFalse(notification.active)

    def test_mark_all_as_read(self):
        self._create_notification()
        self._create_notification()
        self._create_notification()
        self._create_notification()
        self._create_notification()

        self.assertEqual(self.user.notifications.unread(self.user).count(), 5)

        Notification.objects.clear_all(self.user)
        self.assertEqual(self.user.notifications.unread(self.user).count(), 0)

        self.assertEqual(self.user.notifications.read(self.user).count(), 5)

    def test_unsent(self):
        self._create_notification()
        self.assertEqual(self.user.notifications.unsent(self.user).count(), 1)

    def test_sending(self):
        self._create_notification('SEND_EMAIL')
        try:
            self.user.notifications.unsent(self.user).first().send_email()
        except AttributeError:
            self.user.notifications.unsent(self.user).all()[0].send_email()
        self.assertEqual(self.user.notifications.unsent(self.user).count(), 0)
        self.assertEqual(self.user.notifications.sent(self.user).count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_bad_notification_type(self):
        notification = Notification()
        notification.notification_type = 'BAD_TYPE'
        with pytest.raises(KeyError):
            notification.notification_dict

    def test_sending_unmarks_active(self):
        self._create_notification('TEMPORARY')
        try:
            self.user.notifications.unsent(self.user).first().send_email()
        except AttributeError:
            self.user.notifications.unsent(self.user).all()[0].send_email()
        self.assertEqual(Notification.objects.unread(self.user).count(), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_sending_all_unread(self):
        self._create_notification('TEMPORARY')
        self._create_notification('TEMPORARY')
        self._create_notification('TEMPORARY')
        self._create_notification('TEMPORARY')
        self._create_notification('TEMPORARY')

        Notification.objects.send_all_unsent()
        self.assertEqual(Notification.objects.all_unsent().count(), 0)
        self.assertEqual(len(mail.outbox), 5)

    @override_settings(AUTH_USER_MODEL='tests.CustomUser')
    def test_change_email_field(self):
        self.assertIn(
            ('CUSTOM_USER', 'Custom_user'),
            Notification()._meta.get_field_by_name(
                'notification_type')[0].get_choices())
        notification = self._create_notification('CUSTOM_USER')
        self.assertIn('My body:', notification.body)

    def test_using_template_files(self):
        notification = self._create_notification('TEMPLATE_FILES')
        self.assertIn('My headline from file:', notification.headline)
        self.assertIn('My body from file:', notification.body)
