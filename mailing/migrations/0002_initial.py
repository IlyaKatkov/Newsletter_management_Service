# Generated by Django 5.0.1 on 2024-01-29 16:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0002_initial'),
        ('mailing', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mails', related_query_name='mail', to=settings.AUTH_USER_MODEL, verbose_name='владелец рассылки'),
        ),
        migrations.AddField(
            model_name='message',
            name='recipient',
            field=models.ManyToManyField(related_name='clients', to='client.client', verbose_name='клиенты'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='settings', related_query_name='setting', to='mailing.message', verbose_name='рассылка'),
        ),
        migrations.AddField(
            model_name='log',
            name='mailing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mailing.message', verbose_name='рассылка'),
        ),
    ]
