# albums/forms.py
from django import forms
from .models import User

class AlbumSearchForm(forms.Form):
    album_name = forms.CharField(label='Album', max_length=100)

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }


class AlbumForm(forms.Form):
    nombre = forms.CharField(label='Nombre del álbum', max_length=100)
