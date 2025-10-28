import os
import threading
import requests
from django.utils import timezone
from django.db import transaction
from .models import Album, Artist, Label, AlbumArtist, AlbumLabel

TOKEN_DISCOGS = os.getenv('DISCOGS_TOKEN')

DETAIL_URL_TEMPLATE = "https://api.discogs.com/releases/{id}"


def _fetch_release(discogs_id: int):
    try:
        resp = requests.get(DETAIL_URL_TEMPLATE.format(id=discogs_id), params={'token': TOKEN_DISCOGS}, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None


def _upsert_artists(album: Album, data: dict):
    artists = data.get('artists') or []
    order_counter = 1
    for art in artists:
        name = art.get('name')
        if not name:
            continue
        artist_obj, _ = Artist.objects.get_or_create(
            discogs_id=art.get('id'),
            defaults={
                'name': name,
                'real_name': art.get('anv') or '',
                'profile': None
            }
        )
        AlbumArtist.objects.get_or_create(
            album=album,
            artist=artist_obj,
            defaults={'role': 'artist', 'order': order_counter}
        )
        order_counter += 1


def _upsert_labels(album: Album, data: dict):
    labels = data.get('labels') or []
    for lab in labels:
        name = lab.get('name')
        if not name:
            continue
        label_obj, _ = Label.objects.get_or_create(
            discogs_id=lab.get('id'),
            defaults={
                'name': name,
                'catalog_number': lab.get('catno') or ''
            }
        )
        AlbumLabel.objects.get_or_create(
            album=album,
            label=label_obj,
            defaults={'catalog_number': lab.get('catno') or ''}
        )


def _populate_album_fields(album: Album, data: dict):
    album.year = data.get('year') or album.year
    album.country = data.get('country') or album.country
    album.genres = data.get('genres') or album.genres
    album.styles = data.get('styles') or album.styles
    community = data.get('community') or {}
    rating = (community.get('rating') or {}).get('average')
    rating_count = (community.get('rating') or {}).get('count')
    album.average_rating = rating if rating is not None else album.average_rating
    album.rating_count = rating_count if rating_count is not None else album.rating_count
    album.have_count = community.get('have') or album.have_count
    album.want_count = community.get('want') or album.want_count
    album.thumb = data.get('thumb') or album.thumb
    album.cover_image = data.get('images', [{}])[0].get('uri') if data.get('images') else album.cover_image
    formats = data.get('formats') or []
    album.formats = [f.get('name') for f in formats if f.get('name')] or album.formats
    album.discogs_url = data.get('uri') or album.discogs_url
    album.resource_url = data.get('resource_url') or album.resource_url


def _enrich_album(discogs_id: int):
    try:
        album = Album.objects.filter(discogs_id=discogs_id, is_enriched=False).first()
        if not album:
            return
        data = _fetch_release(discogs_id)
        if not data:
            return
        with transaction.atomic():
            _populate_album_fields(album, data)
            _upsert_artists(album, data)
            _upsert_labels(album, data)
            album.is_enriched = True
            album.enrichment_date = timezone.now()
            album.save()
    except Exception:
        # Intentionally swallow exceptions to avoid impacting request thread
        pass


def enqueue_enrichment(discogs_id: int):
    t = threading.Thread(target=_enrich_album, args=(discogs_id,), daemon=True)
    t.start()
