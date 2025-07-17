# albums/views.py
from django.shortcuts import render
import requests
from .forms import AlbumSearchForm

DISCOGS_TOKEN = 'adJIGzPXZSXQcnzMpfLLOGuZgJaTEHjYUUxIvIBY'
DISCOGS_API_URL = 'https://api.discogs.com/database/search'

def get_album_details(album_id):
    """Obtiene los detalles completos de un álbum usando su ID"""
    detail_url = f"https://api.discogs.com/releases/{album_id}"
    detail_params = {'token': DISCOGS_TOKEN}
    detail_resp = requests.get(detail_url, params=detail_params)
    
    if detail_resp.status_code == 200:
        return detail_resp.json()
    return None

def extract_album_info(album_detail):
    """Extrae la información relevante de los detalles del álbum"""
    genero = album_detail.get('genres', [])
    estilos = album_detail.get('styles', [])
    puntuacion = album_detail.get('community', {}).get('rating', {}).get('average', 0)
    cant_puntuaciones = album_detail.get('community', {}).get('rating', {}).get('count', 0)
    artista_principal = album_detail.get('artists', [{}])[0].get('name', '') if album_detail.get('artists') else ''
    
    return genero, estilos, puntuacion, cant_puntuaciones, artista_principal

def process_main_album(album_principal):
    """Procesa el álbum principal y extrae su información"""
    if 'id' in album_principal:
        album_detail = get_album_details(album_principal['id'])
        if album_detail:
            print("Detalles del álbum:", album_detail.get('community', {}))  # Debug
            
            genero, estilos, puntuacion, cant_puntuaciones, artista_principal = extract_album_info(album_detail)
            
            # Actualizar album_principal con información detallada
            album_principal.update({
                'genre': genero,
                'style': estilos,
                'community': album_detail.get('community', {}),
                'artist': artista_principal
            })
            
            return genero, estilos, puntuacion, cant_puntuaciones, artista_principal
        else:
            print("Error obteniendo detalles del álbum")
            return get_fallback_info(album_principal)
    else:
        print("No hay ID disponible para obtener detalles")
        return get_fallback_info(album_principal)

def get_fallback_info(album_principal):
    """Obtiene información básica cuando no se pueden obtener detalles"""
    genero = album_principal.get('genre', [])
    estilos = album_principal.get('style', [])
    artista_principal = album_principal.get('artist', '')
    return genero, estilos, 0, 0, artista_principal

def is_valid_recommendation(disco_detail, estilos, artista_principal, artistas_recomendados):
    """Verifica si un disco cumple con los criterios para ser recomendado"""
    rating = disco_detail.get('community', {}).get('rating', {}).get('average', 0)
    count_ratings = disco_detail.get('community', {}).get('rating', {}).get('count', 0)
    disco_estilos = disco_detail.get('styles', [])
    artista_disco = disco_detail.get('artists', [{}])[0].get('name', '') if disco_detail.get('artists') else ''
    
    # Verificar si TODOS los estilos del disco están en los estilos del álbum principal
    estilos_principales_set = set(estilos)
    disco_estilos_set = set(disco_estilos)
    todos_estilos_coinciden = disco_estilos_set.issubset(estilos_principales_set)
    
    return (rating >= 3.5 and 
            count_ratings > 20 and 
            todos_estilos_coinciden and
            artista_disco != artista_principal and
            artista_disco not in artistas_recomendados), artista_disco

def search_similar_albums(params_similares, album_principal, estilos, artista_principal, artistas_recomendados, recomendaciones, search_type="estilo"):
    """Busca álbumes similares basados en los parámetros dados"""
    resp_similares = requests.get(DISCOGS_API_URL, params=params_similares)
    similares = resp_similares.json().get('results', [])
    
    for disco in similares:
        if 'id' in disco:
            disco_detail = get_album_details(disco['id'])
            
            if disco_detail:
                is_valid, artista_disco = is_valid_recommendation(
                    disco_detail, estilos, artista_principal, artistas_recomendados
                )
                
                if is_valid and disco['title'] != album_principal['title'] and disco not in recomendaciones:
                    # Actualizar disco con información detallada
                    disco.update({
                        'community': disco_detail.get('community', {}),
                        'styles': disco_detail.get('styles', []),
                        'artist': artista_disco
                    })
                    
                    print(f"Disco ({search_type}): {disco['title']}, Artista: {artista_disco}, Rating: {disco_detail.get('community', {}).get('rating', {}).get('average', 0)}")
                    
                    recomendaciones.append(disco)
                    artistas_recomendados.add(artista_disco)
            else:
                print(f"Error obteniendo detalles del disco {disco['title']}")
        
        if len(recomendaciones) >= 3:
            break
    
    return len(recomendaciones) >= 3

def buscar_album(request):
    recomendaciones = []
    artistas_recomendados = set()  # Para evitar artistas duplicados
    
    if request.method == 'POST':
        form = AlbumSearchForm(request.POST)
        if form.is_valid():
            album = form.cleaned_data['album_name']
            params = {
                'q': album,
                'type': 'release',
                'token': DISCOGS_TOKEN
            }
            resp = requests.get(DISCOGS_API_URL, params=params)
            resultados = resp.json().get('results', [])
            
            if resultados:
                album_principal = resultados[0]
                print("Album principal encontrado:", album_principal)  # Debug
                
                # Procesar álbum principal
                genero, estilos, puntuacion, cant_puntuaciones, artista_principal = process_main_album(album_principal)

                # Buscar álbumes similares por estilo
                if estilos:
                    for estilo in estilos:
                        params_similares = {
                            'style': estilo,
                            'genre': genero,
                            'type': 'release',
                            'token': DISCOGS_TOKEN,
                            'sort': 'want',
                            'per_page': 50
                        }
                        
                        if search_similar_albums(params_similares, album_principal, estilos, 
                                               artista_principal, artistas_recomendados, recomendaciones, "estilo"):
                            break
                
                # Si no hay suficientes recomendaciones, buscar por género
                if len(recomendaciones) < 3 and genero:
                    params_similares = {
                        'genre': genero[0],
                        'type': 'release',
                        'token': DISCOGS_TOKEN,
                        'per_page': 50
                    }
                    
                    search_similar_albums(params_similares, album_principal, estilos, 
                                        artista_principal, artistas_recomendados, recomendaciones, "género")

                return render(request, 'albums/resultados.html', {
                    'album_principal': album_principal,
                    'recomendaciones': recomendaciones,
                    'puntuacion_principal': puntuacion,
                    'cant_puntuaciones_principal': cant_puntuaciones,
                })
    else:
        form = AlbumSearchForm()

    return render(request, 'albums/buscar.html', {'form': form})

