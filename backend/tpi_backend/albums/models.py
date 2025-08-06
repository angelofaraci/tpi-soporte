from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    def __str__(self):
        return self.username

class Artist(models.Model):
    discogs_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    real_name = models.CharField(max_length=255, blank=True, null=True)
    profile = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Label(models.Model):
    discogs_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    catalog_number = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    # Identifiers
    discogs_id = models.IntegerField(unique=True, null=True, blank=True)
    master_id = models.IntegerField(null=True, blank=True)
    
    # Basic information
    title = models.CharField(max_length=500)
    artists = models.ManyToManyField(Artist, through='AlbumArtist')
    
    # Release information
    release_date = models.DateField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Musical classification
    genres = models.JSONField(default=list, blank=True)
    styles = models.JSONField(default=list, blank=True)
    
    # Format information
    formats = models.JSONField(default=list, blank=True)  # CD, Vinyl, etc.
    
    # Record labels
    labels = models.ManyToManyField(Label, through='AlbumLabel')
    
    # Community ratings and statistics
    average_rating = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    rating_count = models.IntegerField(default=0)
    have_count = models.IntegerField(default=0)  # How many users have it
    want_count = models.IntegerField(default=0)  # How many users want it
    
    # URLs and resources
    discogs_url = models.URLField(blank=True, null=True)
    resource_url = models.URLField(blank=True, null=True)
    thumb = models.URLField(blank=True, null=True)  # Small image
    cover_image = models.URLField(blank=True, null=True)  # Cover image
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    data_quality = models.CharField(max_length=50, blank=True, null=True)
    
    # Metadata
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    # Relationship with users (favorites)
    favorite_users = models.ManyToManyField(
        User, 
        through='AlbumFavorite',
        related_name='favorite_albums'
    )
    
    class Meta:
        ordering = ['-date_added']
        indexes = [
            models.Index(fields=['discogs_id']),
            models.Index(fields=['title']),
            models.Index(fields=['year']),
            models.Index(fields=['average_rating']),
        ]
    
    def __str__(self):
        return f"{self.title}"

class AlbumArtist(models.Model):
    ROLES = [
        ('artist', 'Main Artist'),
        ('featuring', 'Featuring'),
        ('remix', 'Remix'),
        ('producer', 'Producer'),
        ('composer', 'Composer'),
    ]
    
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='artist')
    order = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['album', 'artist', 'role']
        ordering = ['order']

class AlbumLabel(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    catalog_number = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ['album', 'label']

class AlbumFavorite(models.Model):
    LIST_TYPES = [
        ('favorite', 'Favorite'),
        ('listen_later', 'Listen Later'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    list_type = models.CharField(max_length=20, choices=LIST_TYPES, default='favorite')
    date_added = models.DateTimeField(auto_now_add=True)
    personal_notes = models.TextField(blank=True, null=True)
    personal_rating = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_listened = models.BooleanField(default=False)  # For listen later items
    date_listened = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'album', 'list_type']
        ordering = ['-date_added']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_list_type_display()}: {self.album.title}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_term = models.CharField(max_length=255)
    search_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-search_date']
        unique_together = ['user', 'search_term']  # Prevent duplicate searches per user
    
    def __str__(self):
        return f"{self.user.username}: {self.search_term}"
