import django_filters
from .models import Playlist
from django import forms

class PlaylistFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(
        lookup_expr='icontains', 
        label='Nome da Playlist',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar playlist...'})
    )

    class Meta:
        model = Playlist
        fields = ['nome']