from django.urls import path

from main.apps import MainConfig
from main.views import main

app_name = MainConfig.name

urlpatterns = [
    path('', main, name='home'),
]