from __future__ import absolute_import

from django import test
from django.contrib.auth.models import User
from django.test.utils import override_settings

from heythere.models import Notification, get_notification_types

TEST_NOTIFICATIONS = {
    'CUSTOM_USER': {
        'persistant': True,
        'send_onsite': True,
        'send_email': False,
        'headline_template': 'My headline: {{headline}}',
        'body_template': 'My body: {{body}}',
        'email_field': 'contact'
    }
}


class TestNotificationModel(test.TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser')

    def _create_notification(self, notification_type=None):
        notification_type = notification_type or (
            get_notification_types()[0][0])
        notification = Notification.objects.create_notification(
            user=self.user,
            notification_type=notification_type,
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

    @override_settings(NOTIFICATIONS=TEST_NOTIFICATIONS)
    @override_settings(AUTH_USER_MODEL='tests.CustomUser')
    def test_change_email_field(self):
        self.assertIn(
            ('CUSTOM_USER', 'Custom_user'),
            Notification()._meta.get_field_by_name(
                'notification_type')[0].get_choices())
        notification = Notification.objects.create_notification(
            user=self.user,
            notification_type='CUSTOM_USER',
            headline={'headline': 'This is a notification'},
            body={'body': 'This is the body'}
        )
        # notification = self._create_notification('CUSTOM_USER')
        self.assertIn('My body:', notification.body)
