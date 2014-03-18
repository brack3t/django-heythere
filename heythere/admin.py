from __future__ import absolute_import

import ast

from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .models import Notification, get_notification_types


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification

    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields['notification_type'].choices = get_notification_types()

    def save(self, commit=True):
        obj = super(NotificationForm, self).save(commit=False)
        obj.headline_dict = ast.literal_eval(
            self.cleaned_data['headline_dict'])
        obj.body_dict = ast.literal_eval(self.cleaned_data['body_dict'])
        if commit:
            obj.save()
        return obj


class NotificationAdmin(admin.ModelAdmin):
    def sent(self, obj):
        return bool(obj.sent_at)
    sent.boolean = True

    def send_all_unsent(self, request):
        notifications = Notification.objects.all_unsent()

        if request.method == 'POST' and request.POST.get('post') == 'yes':
            Notification.objects.send_all_unsent()
            self.message_user(
                request,
                'Successfully sent {0} notifications'.format(
                    notifications.count()))
            return redirect('admin:heythere_notification_changelist')

        return TemplateResponse(request, 'admin/send_all_unsent.html', {
            'current_app': self.admin_site.name,
            'opts': self.opts,
            'notifications': notifications
        })

    fieldsets = (
        (None, {
            'fields': (
                'notification_type', 'user',
                'headline', 'headline_dict',
                'body', 'body_dict'
            )
        }),
        ('Details', {
            'fields': ('active', 'sent_at')
        })
    )
    form = NotificationForm
    list_display = ('active', '__unicode__', 'headline', 'body', 'sent')
    list_display_links = ('__unicode__',)
    readonly_fields = ('headline', 'body')

    def get_urls(self):
        admin_send_all_unsent = self.admin_site.admin_view(
            self.send_all_unsent)
        return patterns(
            '',
            url(r'^send_all_unsent/$', admin_send_all_unsent,
                name='heythere_notification_send_all_unsent'),
        ) + super(NotificationAdmin, self).get_urls()

admin.site.register(Notification, NotificationAdmin)
