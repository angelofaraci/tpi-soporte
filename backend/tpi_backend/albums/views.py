# albums/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import requests
from .forms import AlbumSearchForm
from .auth_forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import SearchHistory, Album, AlbumFavorite

TOKEN_DISCOGS = 'adJIGzPXZSXQcnzMpfLLOGuZgJaTEHjYUUxIvIBY'
URL_API_DISCOGS = 'https://api.discogs.com/database/search'

def get_album_details(album_id):

    detail_url = f"https://api.discogs.com/releases/{album_id}"
    detail_params = {'token': TOKEN_DISCOGS}
    detail_response = requests.get(detail_url, params=detail_params)
    
    if detail_response.status_code == 200:
        return detail_response.json()
    return None

def extract_album_information(album_detail):
    
    genre = album_detail.get('genres', [])
    styles = album_detail.get('styles', [])
    rating = album_detail.get('community', {}).get('rating', {}).get('average', 0)
    rating_count = album_detail.get('community', {}).get('rating', {}).get('count', 0)
    main_artist = album_detail.get('artists', [{}])[0].get('name', '') if album_detail.get('artists') else ''
    
    return genre, styles, rating, rating_count, main_artist

def process_main_album(main_album):
   
    if 'id' in main_album:
        album_detail = get_album_details(main_album['id'])
        if album_detail:
            print("Album details:", album_detail.get('community', {}))  # Debug
            
            genre, styles, rating, rating_count, main_artist = extract_album_information(album_detail)
            
            # Update main_album with detailed information
            main_album.update({
                'genre': genre,
                'style': styles,
                'community': album_detail.get('community', {}),
                'artist': main_artist
            })
            
            return genre, styles, rating, rating_count, main_artist
        else:
            print("Error getting album details")
            return get_fallback_information(main_album)
    else:
        print("No ID available to get details")
        return get_fallback_information(main_album)

def get_fallback_information(main_album):
    
    genre = main_album.get('genre', [])
    styles = main_album.get('style', [])
    main_artist = main_album.get('artist', '')
    return genre, styles, 0, 0, main_artist

def is_valid_recommendation(album_detail, styles, main_artist, recommended_artists):
    
    rating = album_detail.get('community', {}).get('rating', {}).get('average', 0)
    rating_count = album_detail.get('community', {}).get('rating', {}).get('count', 0)
    album_styles = album_detail.get('styles', [])
    album_artist = album_detail.get('artists', [{}])[0].get('name', '') if album_detail.get('artists') else ''
    
    # Check if ALL album styles are in the main album styles
    main_styles_set = set(styles)
    album_styles_set = set(album_styles)
    all_styles_match = album_styles_set.issubset(main_styles_set)
    
    return (rating >= 3.5 and 
            rating_count > 20 and 
            all_styles_match and
            album_artist != main_artist and
            album_artist not in recommended_artists), album_artist

def search_similar_albums(similar_params, main_album, styles, main_artist, recommended_artists, recommendations, search_type="style"):
    
    similar_response = requests.get(URL_API_DISCOGS, params=similar_params)
    similar_albums = similar_response.json().get('results', [])
    
    for album in similar_albums:
        if 'id' in album:
            album_detail = get_album_details(album['id'])
            
            if album_detail:
                is_valid, album_artist = is_valid_recommendation(
                    album_detail, styles, main_artist, recommended_artists
                )
                
                if is_valid and album['title'] != main_album['title'] and album not in recommendations:
                    # Update album with detailed information
                    album.update({
                        'community': album_detail.get('community', {}),
                        'styles': album_detail.get('styles', []),
                        'artist': album_artist
                    })
                    
                    print(f"Album ({search_type}): {album['title']}, Artist: {album_artist}, Rating: {album_detail.get('community', {}).get('rating', {}).get('average', 0)}")
                    
                    recommendations.append(album)
                    recommended_artists.add(album_artist)
            else:
                print(f"Error getting album details for {album['title']}")
        
        if len(recommendations) >= 3:
            break
    
    return len(recommendations) >= 3

@login_required
def search_album(request):
    recommendations = []
    recommended_artists = set()  # To avoid duplicate artists
    
    if request.method == 'POST':
        form = AlbumSearchForm(request.POST)
        if form.is_valid():
            album = form.cleaned_data['album_name']
            print(f"Iniciando búsqueda para el álbum: {album}")  # Debug
            
            # Save search to history
            SearchHistory.objects.get_or_create(
                user=request.user,
                search_term=album
            )
            
            params = {
                'q': album,
                'type': 'release',
                'token': TOKEN_DISCOGS
            }
            response = requests.get(URL_API_DISCOGS, params=params)
            results = response.json().get('results', [])
            
            if results:
                main_album = results[0]
                print("Main album found:", main_album)  # Debug
                
               
                genre, styles, rating, rating_count, main_artist = process_main_album(main_album)

                
                if styles:
                    for style in styles:
                        similar_params = {
                            'style': style,
                            'genre': genre,
                            'type': 'release',
                            'token': TOKEN_DISCOGS,
                            'sort': 'want',
                            'per_page': 50
                        }
                        
                        if search_similar_albums(similar_params, main_album, styles, 
                                               main_artist, recommended_artists, recommendations, "style"):
                            break
                
                # If not enough recommendations, search by genre
                if len(recommendations) < 3 and genre:
                    similar_params = {
                        'genre': genre[0],
                        'type': 'release',
                        'token': TOKEN_DISCOGS,
                        'per_page': 50
                    }
                    
                    search_similar_albums(similar_params, main_album, styles, 
                                        main_artist, recommended_artists, recommendations, "genre")
                print("Total recommendations:", len(recommendations))  # Debug
                return render(request, 'albums/resultados.html', {
                    'album_principal': main_album,
                    'recomendaciones': recommendations,
                    'puntuacion_principal': rating,
                    'cant_puntuaciones_principal': rating_count,
                })
    else:
        form = AlbumSearchForm()

    # Get user's search history
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-search_date')[:10]
    
    return render(request, 'albums/buscar.html', {
        'form': form,
        'search_history': search_history
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('buscar_album')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('buscar_album')
        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'albums/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('buscar_album')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Cuenta creada exitosamente! Bienvenido, {user.username}!')
            return redirect('buscar_album')
        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'albums/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión correctamente!')
    return redirect('login')

@login_required
def delete_search_history(request, history_id):
    if request.method == 'POST':
        try:
            history_item = SearchHistory.objects.get(id=history_id, user=request.user)
            history_item.delete()
            return JsonResponse({'success': True})
        except SearchHistory.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Historial no encontrado'})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def add_to_listen_later(request):
    if request.method == 'POST':
        import json
        try:
            # Get album data from the request
            album_data = json.loads(request.body)
            discogs_id = album_data.get('discogs_id')
            title = album_data.get('title', '')
            artist = album_data.get('artist', '')
            year = album_data.get('year', '')
            
            # Create or get the album
            album, created = Album.objects.get_or_create(
                discogs_id=discogs_id,
                defaults={
                    'title': title,
                    'year': year if year else None,
                }
            )
            
            # Add to listen later list
            album_favorite, created = AlbumFavorite.objects.get_or_create(
                user=request.user,
                album=album,
                list_type='listen_later'
            )
            
            if created:
                return JsonResponse({
                    'success': True, 
                    'message': f'"{title}" added to Listen Later list!'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': f'"{title}" is already in your Listen Later list.'
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def listen_later_list(request):
    listen_later_albums = AlbumFavorite.objects.filter(user=request.user, list_type='listen_later')
    return render(request, 'albums/listen_later.html', {
        'listen_later_albums': listen_later_albums
    })

@login_required
def remove_from_listen_later(request, listen_later_id):
    if request.method == 'POST':
        try:
            listen_later_item = AlbumFavorite.objects.get(
                id=listen_later_id, 
                user=request.user,
                list_type='listen_later'
            )
            album_title = listen_later_item.album.title
            listen_later_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'"{album_title}" removed from Listen Later list.'
            })
        except AlbumFavorite.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Album not found in your Listen Later list.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def mark_as_listened(request, listen_later_id):
    if request.method == 'POST':
        try:
            from django.utils import timezone
            listen_later_item = AlbumFavorite.objects.get(
                id=listen_later_id, 
                user=request.user,
                list_type='listen_later'
            )
            listen_later_item.is_listened = True
            listen_later_item.date_listened = timezone.now()
            listen_later_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'"{listen_later_item.album.title}" marked as listened!'
            })
        except AlbumFavorite.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Album not found in your Listen Later list.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def mark_as_not_listened(request, listen_later_id):
    if request.method == 'POST':
        try:
            listen_later_item = AlbumFavorite.objects.get(
                id=listen_later_id, 
                user=request.user,
                list_type='listen_later'
            )
            listen_later_item.is_listened = False
            listen_later_item.date_listened = None
            listen_later_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'"{listen_later_item.album.title}" marked as not listened!'
            })
        except AlbumFavorite.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Album not found in your Listen Later list.'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def buscando_view(request):
    return render(request, 'albums/buscando.html')

