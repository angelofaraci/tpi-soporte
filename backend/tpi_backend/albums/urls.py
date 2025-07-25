# albums/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_album, name='buscar_album'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-history/<int:history_id>/', views.delete_search_history, name='delete_search_history'),
]
