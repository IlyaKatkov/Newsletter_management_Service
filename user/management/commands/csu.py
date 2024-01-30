from django.core.management.base import BaseCommand
from user.models import User
import os


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email='AlmazCool@mail.ru',
            first_name='Admin',
            last_name='SkyPro',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        user.set_password(os.getenv('PASSWORD'))
        user.save()