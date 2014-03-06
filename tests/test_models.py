from __future__ import absolute_import

from django import test
from django.contrib.auth.models import User

from heythere.models import Notification, NOTIFICATION_TYPES


class TestNotificationModel(test.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser')

    def _create_notification(self):
        notification = Notification.objects.create_notification(
            user=self.user,
            notification_type=NOTIFICATION_TYPES[0][0],
            headline={'headline': 'This is a notification'},
            body={'body': 'This is the body'}
        )
        return notification

    def test_basic_notification(self):
        notification = self._create_notification()

        self.assertTrue(notification.active)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.headline, 'This is a notification')
        self.assertIn(notification.user.__unicode__(),
                      notification.__unicode__())

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
