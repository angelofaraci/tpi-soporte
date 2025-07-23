# albums/views.py
from django.shortcuts import render
import requests
from .forms import AlbumSearchForm

TOKEN_DISCOGS = 'adJIGzPXZSXQcnzMpfLLOGuZgJaTEHjYUUxIvIBY'
URL_API_DISCOGS = 'https://api.discogs.com/database/search'

def obtener_detalles_album(id_album):

    url_detalle = f"https://api.discogs.com/releases/{id_album}"
    parametros_detalle = {'token': TOKEN_DISCOGS}
    respuesta_detalle = requests.get(url_detalle, params=parametros_detalle)
    
    if respuesta_detalle.status_code == 200:
        return respuesta_detalle.json()
    return None

def extraer_informacion_album(detalle_album):
    
    genero = detalle_album.get('genres', [])
    estilos = detalle_album.get('styles', [])
    puntuacion = detalle_album.get('community', {}).get('rating', {}).get('average', 0)
    cant_puntuaciones = detalle_album.get('community', {}).get('rating', {}).get('count', 0)
    artista_principal = detalle_album.get('artists', [{}])[0].get('name', '') if detalle_album.get('artists') else ''
    
    return genero, estilos, puntuacion, cant_puntuaciones, artista_principal

def procesar_album_principal(album_principal):
   
    if 'id' in album_principal:
        detalle_album = obtener_detalles_album(album_principal['id'])
        if detalle_album:
            print("Detalles del álbum:", detalle_album.get('community', {}))  # Debug
            
            genero, estilos, puntuacion, cant_puntuaciones, artista_principal = extraer_informacion_album(detalle_album)
            
            # Actualizar album_principal con información detallada
            album_principal.update({
                'genre': genero,
                'style': estilos,
                'community': detalle_album.get('community', {}),
                'artist': artista_principal
            })
            
            return genero, estilos, puntuacion, cant_puntuaciones, artista_principal
        else:
            print("Error obteniendo detalles del álbum")
            return obtener_informacion_respaldo(album_principal)
    else:
        print("No hay ID disponible para obtener detalles")
        return obtener_informacion_respaldo(album_principal)

def obtener_informacion_respaldo(album_principal):
    
    genero = album_principal.get('genre', [])
    estilos = album_principal.get('style', [])
    artista_principal = album_principal.get('artist', '')
    return genero, estilos, 0, 0, artista_principal

def es_recomendacion_valida(detalle_disco, estilos, artista_principal, artistas_recomendados):
    
    calificacion = detalle_disco.get('community', {}).get('rating', {}).get('average', 0)
    cantidad_calificaciones = detalle_disco.get('community', {}).get('rating', {}).get('count', 0)
    estilos_disco = detalle_disco.get('styles', [])
    artista_disco = detalle_disco.get('artists', [{}])[0].get('name', '') if detalle_disco.get('artists') else ''
    
    # Verificar si TODOS los estilos del disco están en los estilos del álbum principal
    conjunto_estilos_principales = set(estilos)
    conjunto_estilos_disco = set(estilos_disco)
    todos_estilos_coinciden = conjunto_estilos_disco.issubset(conjunto_estilos_principales)
    
    return (calificacion >= 3.5 and 
            cantidad_calificaciones > 20 and 
            todos_estilos_coinciden and
            artista_disco != artista_principal and
            artista_disco not in artistas_recomendados), artista_disco

def buscar_albums_similares(parametros_similares, album_principal, estilos, artista_principal, artistas_recomendados, recomendaciones, tipo_busqueda="estilo"):
    
    respuesta_similares = requests.get(URL_API_DISCOGS, params=parametros_similares)
    similares = respuesta_similares.json().get('results', [])
    
    for disco in similares:
        if 'id' in disco:
            detalle_disco = obtener_detalles_album(disco['id'])
            
            if detalle_disco:
                es_valida, artista_disco = es_recomendacion_valida(
                    detalle_disco, estilos, artista_principal, artistas_recomendados
                )
                
                if es_valida and disco['title'] != album_principal['title'] and disco not in recomendaciones:
                    # Actualizar disco con información detallada
                    disco.update({
                        'community': detalle_disco.get('community', {}),
                        'styles': detalle_disco.get('styles', []),
                        'artist': artista_disco
                    })
                    
                    print(f"Disco ({tipo_busqueda}): {disco['title']}, Artista: {artista_disco}, Rating: {detalle_disco.get('community', {}).get('rating', {}).get('average', 0)}")
                    
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
        formulario = AlbumSearchForm(request.POST)
        if formulario.is_valid():
            album = formulario.cleaned_data['album_name']
            parametros = {
                'q': album,
                'type': 'release',
                'token': TOKEN_DISCOGS
            }
            respuesta = requests.get(URL_API_DISCOGS, params=parametros)
            resultados = respuesta.json().get('results', [])
            
            if resultados:
                album_principal = resultados[0]
                print("Album principal encontrado:", album_principal)  # Debug
                
               
                genero, estilos, puntuacion, cant_puntuaciones, artista_principal = procesar_album_principal(album_principal)

                
                if estilos:
                    for estilo in estilos:
                        parametros_similares = {
                            'style': estilo,
                            'genre': genero,
                            'type': 'release',
                            'token': TOKEN_DISCOGS,
                            'sort': 'want',
                            'per_page': 50
                        }
                        
                        if buscar_albums_similares(parametros_similares, album_principal, estilos, 
                                                 artista_principal, artistas_recomendados, recomendaciones, "estilo"):
                            break
                
                # Si no hay suficientes recomendaciones, buscar por género
                if len(recomendaciones) < 3 and genero:
                    parametros_similares = {
                        'genre': genero[0],
                        'type': 'release',
                        'token': TOKEN_DISCOGS,
                        'per_page': 50
                    }
                    
                    buscar_albums_similares(parametros_similares, album_principal, estilos, 
                                          artista_principal, artistas_recomendados, recomendaciones, "género")

                return render(request, 'albums/resultados.html', {
                    'album_principal': album_principal,
                    'recomendaciones': recomendaciones,
                    'puntuacion_principal': puntuacion,
                    'cant_puntuaciones_principal': cant_puntuaciones,
                })
    else:
        formulario = AlbumSearchForm()

    return render(request, 'albums/buscar.html', {'form': formulario})

