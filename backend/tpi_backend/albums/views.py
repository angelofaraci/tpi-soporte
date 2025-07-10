# albums/views.py
from django.shortcuts import render
import requests
from .forms import AlbumSearchForm

DISCOGS_TOKEN = 'adJIGzPXZSXQcnzMpfLLOGuZgJaTEHjYUUxIvIBY'
DISCOGS_API_URL = 'https://api.discogs.com/database/search'

def buscar_album(request):
    recomendaciones = []
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
                album_principal = resultados[0]  # El mejor match
                genero = album_principal.get('genre', [])
                puntuacion = album_principal.get('community', {}).get('rating', {}).get('average', 0)

                # Segunda búsqueda: encontrar discos similares
                params_similares = {
                    'genre': genero[0] if genero else '',
                    'type': 'release',
                    'token': DISCOGS_TOKEN
                }
                resp_similares = requests.get(DISCOGS_API_URL, params=params_similares)
                similares = resp_similares.json().get('results', [])

                # Filtrar por puntuación
                for disco in similares:
                    rating = disco.get('community', {}).get('rating', {}).get('average', 0)
                    if rating >= puntuacion and disco['title'] != album_principal['title']:
                        recomendaciones.append(disco)
                    if len(recomendaciones) >= 3:
                        break

                return render(request, 'albums/resultados.html', {
                    'album_principal': album_principal,
                    'recomendaciones': recomendaciones,
                })
    else:
        form = AlbumSearchForm()

    return render(request, 'albums/buscar.html', {'form': form})
