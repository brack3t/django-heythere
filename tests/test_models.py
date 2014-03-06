from __future__ import absolute_import

from django import test
from django.contrib.auth.models import User

from heythere.models import Notification, NOTIFICATION_TYPES


class TestNotificationModel(test.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser')

    def test_basic_notification(self):
        notification = Notification.objects.create_notification(
            user=self.user,
            notification_type=NOTIFICATION_TYPES[0][0],
            headline={'headline': 'This is a notification'},
            body={'body': 'This is the body'}
        )
        self.assertTrue(notification.active)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.headline, 'This is a notification')
        self.assertIn(notification.user.__unicode__(),
                      notification.__unicode__())
