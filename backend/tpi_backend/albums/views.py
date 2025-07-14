# albums/views.py
from django.shortcuts import render
import requests
from .forms import AlbumSearchForm

DISCOGS_TOKEN = 'adJIGzPXZSXQcnzMpfLLOGuZgJaTEHjYUUxIvIBY'
DISCOGS_API_URL = 'https://api.discogs.com/database/search'

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
                
                # Obtener información detallada del álbum principal
                if 'id' in album_principal:
                    detail_url = f"https://api.discogs.com/releases/{album_principal['id']}"
                    detail_params = {'token': DISCOGS_TOKEN}
                    detail_resp = requests.get(detail_url, params=detail_params)
                    if detail_resp.status_code == 200:
                        album_detail = detail_resp.json()
                        print("Detalles del álbum:", album_detail.get('community', {}))  # Debug
                        
                        # Extraer información del álbum detallado
                        genero = album_detail.get('genres', [])
                        estilos = album_detail.get('styles', [])
                        puntuacion = album_detail.get('community', {}).get('rating', {}).get('average', 0)
                        cant_puntuaciones = album_detail.get('community', {}).get('rating', {}).get('count', 0)
                        artista_principal = album_detail.get('artists', [{}])[0].get('name', '') if album_detail.get('artists') else ''
                        
                        # Actualizar album_principal con información detallada
                        album_principal.update({
                            'genre': genero,
                            'style': estilos,
                            'community': album_detail.get('community', {}),
                            'artist': artista_principal
                        })
                    else:
                        print("Error obteniendo detalles del álbum:", detail_resp.status_code)
                        # Fallback a la información básica de búsqueda
                        genero = album_principal.get('genre', [])
                        estilos = album_principal.get('style', [])
                        puntuacion = 0
                        cant_puntuaciones = 0
                        artista_principal = album_principal.get('artist', '')
                else:
                    print("No hay ID disponible para obtener detalles")
                    genero = album_principal.get('genre', [])
                    estilos = album_principal.get('style', [])
                    puntuacion = 0
                    cant_puntuaciones = 0
                    artista_principal = album_principal.get('artist', '')

                # Segunda búsqueda: encontrar discos similares
                # Primero buscamos por estilo (más específico que género)
                if estilos:
                    for estilo in estilos:
                        params_similares = {
                            'style': estilo,
                            'genre': genero,
                            'type': 'release',
                            'token': DISCOGS_TOKEN,
                            'sort': 'want',
                            'per_page': 50  # Obtener más resultados para filtrar mejor
                        }
                        resp_similares = requests.get(DISCOGS_API_URL, params=params_similares)
                        similares = resp_similares.json().get('results', [])
                        
                        # Filtrar por puntuación, cantidad de ratings y título diferente
                        for disco in similares:
                            # Obtener información detallada de cada disco
                            if 'id' in disco:
                                detail_url = f"https://api.discogs.com/releases/{disco['id']}"
                                detail_params = {'token': DISCOGS_TOKEN}
                                detail_resp = requests.get(detail_url, params=detail_params)
                                
                                if detail_resp.status_code == 200:
                                    disco_detail = detail_resp.json()
                                    rating = disco_detail.get('community', {}).get('rating', {}).get('average', 0)
                                    count_ratings = disco_detail.get('community', {}).get('rating', {}).get('count', 0)
                                    disco_estilos = disco_detail.get('styles', [])
                                    artista_disco = disco_detail.get('artists', [{}])[0].get('name', '') if disco_detail.get('artists') else ''
                                    
                                    # Actualizar disco con información detallada
                                    disco.update({
                                        'community': disco_detail.get('community', {}),
                                        'styles': disco_estilos,
                                        'artist': artista_disco
                                    })
                                    
                                    # Verificar si TODOS los estilos del disco están en los estilos del álbum principal
                                    estilos_principales_set = set(estilos)
                                    disco_estilos_set = set(disco_estilos)
                                    todos_estilos_coinciden = disco_estilos_set.issubset(estilos_principales_set)
                                    
                                    print(f"Disco: {disco['title']}, Artista: {artista_disco}, Rating: {rating}, Count: {count_ratings}, Estilos del disco: {disco_estilos}, Estilos principales: {estilos}, Todos coinciden: {todos_estilos_coinciden}")  # Debug
                                    
                                    # Condiciones mejoradas: rating >= 3.5, más de 20 ratings, título diferente, TODOS los estilos coinciden, artista diferente y no repetido
                                    if (rating >= 3.5 and 
                                        count_ratings > 20 and 
                                        disco['title'] != album_principal['title'] and
                                        todos_estilos_coinciden and  # TODOS los estilos del disco deben estar en el álbum principal
                                        artista_disco != artista_principal and  # No debe ser el mismo artista del álbum principal
                                        artista_disco not in artistas_recomendados and  # No debe ser un artista ya recomendado
                                        disco not in recomendaciones):  # Evitar duplicados
                                        recomendaciones.append(disco)
                                        artistas_recomendados.add(artista_disco)  # Agregar artista al set de recomendados
                                else:
                                    print(f"Error obteniendo detalles del disco {disco['title']}: {detail_resp.status_code}")
                            
                            if len(recomendaciones) >= 3:
                                break
                        
                        if len(recomendaciones) >= 3:
                            break
                
                # Si no hay suficientes recomendaciones con estilos, buscar por género
                if len(recomendaciones) < 3 and genero:
                    params_similares = {
                        'genre': genero[0],
                        'type': 'release',
                        'token': DISCOGS_TOKEN,
                        'per_page': 50
                    }
                    resp_similares = requests.get(DISCOGS_API_URL, params=params_similares)
                    similares = resp_similares.json().get('results', [])
                    
                    for disco in similares:
                        # Obtener información detallada de cada disco
                        if 'id' in disco:
                            detail_url = f"https://api.discogs.com/releases/{disco['id']}"
                            detail_params = {'token': DISCOGS_TOKEN}
                            detail_resp = requests.get(detail_url, params=detail_params)
                            
                            if detail_resp.status_code == 200:
                                disco_detail = detail_resp.json()
                                rating = disco_detail.get('community', {}).get('rating', {}).get('average', 0)
                                count_ratings = disco_detail.get('community', {}).get('rating', {}).get('count', 0)
                                disco_estilos = disco_detail.get('styles', [])
                                artista_disco = disco_detail.get('artists', [{}])[0].get('name', '') if disco_detail.get('artists') else ''
                                
                                # Actualizar disco con información detallada
                                disco.update({
                                    'community': disco_detail.get('community', {}),
                                    'styles': disco_estilos,
                                    'artist': artista_disco
                                })
                                
                                # Verificar si TODOS los estilos del disco están en los estilos del álbum principal
                                estilos_principales_set = set(estilos)
                                disco_estilos_set = set(disco_estilos)
                                todos_estilos_coinciden = disco_estilos_set.issubset(estilos_principales_set)
                                
                                print(f"Disco (género): {disco['title']}, Artista: {artista_disco}, Rating: {rating}, Count: {count_ratings}, Estilos del disco: {disco_estilos}, Estilos principales: {estilos}, Todos coinciden: {todos_estilos_coinciden}")  # Debug
                                
                                # Condiciones mejoradas: rating >= 3.5, más de 20 ratings, título diferente, TODOS los estilos coinciden, artista diferente y no repetido
                                if (rating >= 3.5 and 
                                    count_ratings > 20 and 
                                    disco['title'] != album_principal['title'] and
                                    todos_estilos_coinciden and  # TODOS los estilos del disco deben estar en el álbum principal
                                    artista_disco != artista_principal and  # No debe ser el mismo artista del álbum principal
                                    artista_disco not in artistas_recomendados and  # No debe ser un artista ya recomendado
                                    disco not in recomendaciones):
                                    recomendaciones.append(disco)
                                    artistas_recomendados.add(artista_disco)  # Agregar artista al set de recomendados
                            else:
                                print(f"Error obteniendo detalles del disco {disco['title']}: {detail_resp.status_code}")
                        
                        if len(recomendaciones) >= 3:
                            break

                return render(request, 'albums/resultados.html', {
                    'album_principal': album_principal,
                    'recomendaciones': recomendaciones,
                    'puntuacion_principal': puntuacion,
                    'cant_puntuaciones_principal': cant_puntuaciones,
                })
    else:
        form = AlbumSearchForm()

    return render(request, 'albums/buscar.html', {'form': form})

