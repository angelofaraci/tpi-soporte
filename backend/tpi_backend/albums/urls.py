# albums/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_album, name='buscar_album'),
]
