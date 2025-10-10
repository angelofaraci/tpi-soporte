# albums/urls.py
from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Root URL redirects to buscar_album
    path('', lambda request: redirect('buscar_album'), name='home'),
    path('buscar_album/', views.search_album, name='buscar_album'),
    path('buscando/', views.buscando_view, name='buscando'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('delete-history/<int:history_id>/', views.delete_search_history, name='delete_search_history'),
    path('listen-later/', views.listen_later_list, name='listen_later_list'),
    path('add-to-listen-later/', views.add_to_listen_later, name='add_to_listen_later'),
    path('remove-from-listen-later/<int:listen_later_id>/', views.remove_from_listen_later, name='remove_from_listen_later'),
    path('mark-as-listened/<int:listen_later_id>/', views.mark_as_listened, name='mark_as_listened'),
    path('mark-as-not-listened/<int:listen_later_id>/', views.mark_as_not_listened, name='mark_as_not_listened'),
    path('ai/album-description/', views.album_description_api, name='album_description_api'),
]
