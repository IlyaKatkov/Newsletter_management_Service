from django.db import models
from client.models import Client
from config import settings


NULLABLE = {'blank': True, 'null': True }



class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='тема письма')
    body = models.TextField(**NULLABLE, verbose_name='тело письма')
    recipient = models.ManyToManyField(Client, related_name='clients', verbose_name='клиенты')
    is_published = models.BooleanField(default=True, verbose_name='опубликована')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mails', related_query_name="mail", **NULLABLE, verbose_name='владелец рассылки')

    def __str__(self):
        return f'{self.subject}'

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        permissions = [
            ('can_cancel_mailing', 'Может отменять публикацию рассылки'),
        ]

class Mailing(models.Model):
    class FREQUENCY_CHOICES(models.TextChoices):
            DAILY = 'daily', 'Ежедневно'
            WEEKLY = 'weekly', 'Еженедельно'
            MONTHLY = 'monthly', 'Ежемесячно'

    class MAILING_STATUS(models.TextChoices):
         COMPLETED = 'completed', 'завершена'
         CREATED = 'created', 'создана'
         LAUNCHED = 'launched', 'запущена'

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='settings', related_query_name="setting", verbose_name='рассылка')
    start_time = models.DateField(verbose_name='начало рассылки')
    finish_time = models.DateField(verbose_name='окончание рассылки')
    frequency = models.CharField(max_length=300, choices=FREQUENCY_CHOICES.choices, verbose_name='периодичность')
    mailing_status = models.CharField(max_length=300, choices=MAILING_STATUS.choices, verbose_name='статус рассылки')
    next_sending_date = models.DateField(**NULLABLE, verbose_name='следующая отправка')
    client = models.ManyToManyField(Client, verbose_name='получатели')


    def __str__(self):
        return f'{self.start_time} - {self.finish_time}'


    class Meta:
        verbose_name = 'рассылку'
        verbose_name_plural = 'рассылки'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.next_sending_date:
            self.next_sending_date = self.start_time

    def save(self, *args, **kwargs):
        if not self.next_sending_date:
            self.next_sending_date = self.start_time
        super().save(*args, **kwargs)

    def get_mailing_status_display(self):
        return dict(self.MAILING_STATUS.choices).get(self.mailing_status, 'Черновик')

    def get_mailing_period_display(self):
        return dict(self.FREQUENCY_CHOICES.choices).get(self.frequency, 'Не указано')


class Log(models.Model):
    class STATUS(models.TextChoices):
        SUCCESS = 'Успешно'
        FAILED = 'Пррвально'

    datatime = models.DateTimeField(**NULLABLE, verbose_name='дата посылки')
    mailing = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='рассылка')
    status = models.CharField(max_length=20, choices=STATUS.choices, **NULLABLE, verbose_name='статус посылки')
    answer_mail_server = models.TextField(max_length=150, **NULLABLE, verbose_name='ответ почтового сервера')

    def __str__(self):
        return f'{self.datatime} - {self.status}'

    class Meta:
        verbose_name = 'лог'
        verbose_name_plural = 'логи'
