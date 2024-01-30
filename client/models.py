from django.db import models

from config import settings

NULLABLE = {'blank': True, 'null': True }

class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='email')
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    comment = models.TextField(verbose_name='комментарий', **NULLABLE)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clients', related_query_name='client', **NULLABLE, verbose_name='владелец списка рассылки')

    def __str__(self):
        return f'{self.full_name}: {self.email}'

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

