from __future__ import absolute_import

import ast

from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

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

    def handle_sending_all_unsent(self, request):
        notifications = Notification.objects.all_unsent()

        if request.method == 'POST' and request.POST.get('post') == 'yes':
            Notification.objects.send_all_unsent()
            self.message_user(
                request,
                _(u'Successfully tried to send {0} notifications'.format(
                    notifications.count())))
            return redirect('admin:heythere_notification_changelist')

        return TemplateResponse(request, 'admin/send_all_unsent.html', {
            'current_app': self.admin_site.name,
            'opts': self.opts,
            'notifications': notifications
        })

    def send_selected(self, request, queryset):
        if request.POST.get('post'):
            for notification in queryset:
                notification.send_email()
            self.message_user(
                request,
                _(u'Successfully tried to send {0} notifications'.format(
                    len(queryset))))
            return redirect('admin:heythere_notification_changelist')
        return TemplateResponse(request, 'admin/send_selected.html', {
            'current_app': self.admin_site.name,
            'opts': self.opts,
            'action_checkbox_name': admin.ACTION_CHECKBOX_NAME,
            'queryset': queryset
        })
    send_selected.short_description = _(u'Send selected notifications')

    actions = ['send_selected']
    fieldsets = (
        (None, {
            'fields': (
                'notification_type', 'user',
                'headline', 'headline_dict',
                'body', 'body_dict'
            )
        }),
        (_(u'Details'), {
            'fields': ('active', 'sent_at')
        })
    )
    form = NotificationForm
    list_display = ('active', '__unicode__', 'headline', 'body', 'sent')
    list_display_links = ('__unicode__',)
    readonly_fields = ('headline', 'body')

    def get_urls(self):
        admin_send_all_unsent = self.admin_site.admin_view(
            self.handle_sending_all_unsent)
        return patterns(
            '',
            url(r'^send_all_unsent/$', admin_send_all_unsent,
                name='heythere_notification_send_all_unsent'),
        ) + super(NotificationAdmin, self).get_urls()

admin.site.register(Notification, NotificationAdmin)
