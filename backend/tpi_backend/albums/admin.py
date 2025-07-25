from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Artist, Label, Album, AlbumArtist, AlbumLabel, AlbumFavorite, SearchHistory

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar',)}),
    )

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'real_name', 'discogs_id')
    search_fields = ('name', 'real_name')
    list_filter = ('discogs_id',)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'catalog_number', 'discogs_id')
    search_fields = ('name', 'catalog_number')

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'average_rating', 'rating_count', 'date_added')
    list_filter = ('year', 'genres', 'country', 'date_added')
    search_fields = ('title',)
    readonly_fields = ('date_added', 'date_updated')

@admin.register(AlbumFavorite)
class AlbumFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'personal_rating', 'date_added')
    list_filter = ('personal_rating', 'date_added')
    search_fields = ('user__username', 'album__title')

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_term', 'search_date')
    list_filter = ('search_date',)
    search_fields = ('user__username', 'search_term')
