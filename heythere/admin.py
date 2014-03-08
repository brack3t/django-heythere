from __future__ import absolute_import

import ast

from django import forms
from django.contrib import admin

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

admin.site.register(Notification, NotificationAdmin)
