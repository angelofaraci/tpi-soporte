# albums/forms.py
from django import forms

class AlbumSearchForm(forms.Form):
    album_name = forms.CharField(label='Álbum', max_length=100)


class AlbumForm(forms.Form):
    nombre = forms.CharField(label='Nombre del álbum', max_length=100)
