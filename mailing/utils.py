from django.core.mail import send_mail

import config.settings
from mailing.models import Message, Mailing


def get_mail_prepared(current_date):
    new_mail = Message.objects.filter(is_published=True, setting__mailing_status=Mailing.MAILING_STATUS.CREATED, setting__mailing_start__lte=current_date, setting__mailing_end__gte=current_date)

    old_mail = Message.objects.filter(is_published=True, setting__mailing_status=Mailing.MAILING_STATUS.LAUNCHED, setting__mailing_end__lt=current_date)

    if new_mail.exists():
        for letter in new_mail:
            settings = letter.settings.filter(message_id=letter.pk)
            for setting in settings:
                setting.mailing_status = Mailing.MAILING_STATUS.LAUNCHED
                setting.save()

    if old_mail.exists():
        for letter in old_mail:
            settings = letter.settings.filter(message_id=letter.pk)
            for setting in settings:
                setting.mailing_status = Mailing.MAILING_STATUS.COMPLETED
                setting.save()

    running_mail = Message.objects.filter(is_published=True, setting__mailing_status=Mailing.MAILING_STATUS.LAUNCHED)

    return running_mail


def get_current_mail_for_sending_in_period(current_date, mail_queryset, frequency):
    current_mail_for_sending_in_period = mail_queryset.filter(setting__mailing_period=frequency,
                                                              setting__next_sending_date=current_date)

    return current_mail_for_sending_in_period


def send_ready_mail(all_mail):
    for recipient in all_mail.recipient.all():
        send_mail(
            subject=all_mail.subject,
            message=all_mail.body,
            from_email=config.settings.HOST_USER,
            recipient_list=[recipient]
        )