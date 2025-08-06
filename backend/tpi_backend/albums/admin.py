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
    list_display = ('user', 'album', 'list_type', 'date_added', 'is_listened', 'personal_rating')
    list_filter = ('list_type', 'is_listened', 'date_added', 'personal_rating')
    search_fields = ('user__username', 'album__title')
    actions = ['mark_as_listened', 'mark_as_not_listened', 'move_to_favorites', 'move_to_listen_later']
    
    def mark_as_listened(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(list_type='listen_later').update(is_listened=True, date_listened=timezone.now())
        self.message_user(request, f'{updated} albums marked as listened.')
    mark_as_listened.short_description = "Mark selected listen later albums as listened"
    
    def mark_as_not_listened(self, request, queryset):
        updated = queryset.filter(list_type='listen_later').update(is_listened=False, date_listened=None)
        self.message_user(request, f'{updated} albums marked as not listened.')
    mark_as_not_listened.short_description = "Mark selected albums as not listened"
    
    def move_to_favorites(self, request, queryset):
        updated = queryset.update(list_type='favorite')
        self.message_user(request, f'{updated} albums moved to favorites.')
    move_to_favorites.short_description = "Move selected albums to favorites"
    
    def move_to_listen_later(self, request, queryset):
        updated = queryset.update(list_type='listen_later')
        self.message_user(request, f'{updated} albums moved to listen later.')
    move_to_listen_later.short_description = "Move selected albums to listen later"

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_term', 'search_date')
    list_filter = ('search_date',)
    search_fields = ('user__username', 'search_term')
