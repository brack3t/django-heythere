from __future__ import absolute_import

from django.core.management.base import BaseCommand

from heythere.models import Notification


class Command(BaseCommand):
    help = 'Sends all unsent notifications.'

    def handle(self, *args, **options):
        note_count = Notification.objects.unsent().count()
        Notification.objects.send_all_new()
        self.stdout.write(
            u'Successfully sent {0} notifications'.format(note_count))
