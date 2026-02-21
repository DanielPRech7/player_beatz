import django_filters
from .models import Playlist
from django import forms

class PlaylistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Playlist Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search playlist...'})
    )

    class Meta:
        model = Playlist
        fields = ['name']