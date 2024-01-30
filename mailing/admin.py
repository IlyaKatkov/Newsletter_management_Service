from django.contrib import admin
from mailing.models import Mailing, Message


class MailingSettingsInline(admin.StackedInline):
    model = Mailing
    extra = 1
    can_delete = False
    verbose_name = 'настройки рассылки'
    verbose_name_plural = 'настройки рассылок'


@admin.register(Message)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner',)
    list_filter = ('owner',)
    inlines = [
        MailingSettingsInline,
    ]
