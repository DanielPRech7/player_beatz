from django.contrib import admin
from .models import Musica, Playlist

@admin.register(Musica)
class MusicaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'artista', 'youtube_id')
    search_fields = ('titulo', 'artista')

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    filter_horizontal = ('musicas',)