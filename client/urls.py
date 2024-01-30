from django.urls import path

from client.apps import ClientConfig
from client.views import *

app_name = ClientConfig.name

urlpatterns = [
    path('view_all/', ClientListView.as_view(), name='list_clients'),
    path('create/', ClientCreateView.as_view(), name='create_client'),
    path('update/<int:pk>/', ClientUpdateView.as_view(), name='update_client'),
    path('delete/<int:pk>/', ClientDeleteView.as_view(), name='delete_client'),
]