import datetime
import smtplib

import pytz
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from mailing.models import Mailing, Log
from mailing.utils import get_mail_prepared, send_ready_mail


class Command(BaseCommand):
    def handle(self, *args, **options):

        curr_date = datetime.datetime.now().date()

        mail_to_handle = get_mail_prepared(curr_date).filter(setting__next_sending_date=curr_date)

        for mail in mail_to_handle:
            try:
                send_ready_mail(mail)
                status = Log.STATUS.SUCCESS
                error_message = ''
            except smtplib.SMTPException as e:
                status = Log.STATUS.FAILED
                if 'authentication failed' in str(e):
                    error_message = 'Ошибка аутентификации на сервисе'
                elif 'suspicion of SPAM' in str(e):
                    error_message = 'Слишком много рассылок, сервис отклонил письмо'
                else:
                    error_message = e
            finally:
                og.objects.create(
                    status=status,
                    message=error_message,
                    date=datetime.datetime.now().replace(tzinfo=pytz.UTC),
                    mailing=mail
                )

            for setting in mail.settings.filter(message_id=mail.pk):
                if setting.mailing_period == Mailing.FREQUENCY_CHOICES.DAILY:
                    setting.next_sending_date += datetime.timedelta(days=1)
                elif setting.mailing_period == Mailing.FREQUENCY_CHOICES.WEEKLY:
                    setting.next_sending_date += datetime.timedelta(weeks=1)
                elif setting.mailing_period == Mailing.FREQUENCY_CHOICES.MONTHLY:
                    setting.next_sending_date = curr_date + relativedelta(months=+1)
                setting.save()