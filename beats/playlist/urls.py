from django.urls import path
from .views import (
    PlaylistListView,
    PlaylistDetailView,
    PlaylistCreateView,
    PlaylistAddMusicaView,
    PlaylistShareView,
    PlaylistUpdateCapaView,
    atualizar_tempo_playlist,
    favoritar_playlist,
)

urlpatterns = [
    path('', PlaylistListView.as_view(), name='playlist_list'),
    path('<int:pk>/', PlaylistDetailView.as_view(), name='playlist_detail'), 
    path('<int:pk>/adicionar-musica/', PlaylistAddMusicaView.as_view(), name='adicionar_musica_playlist'),
    path('<int:pk>/compartilhar/', PlaylistShareView.as_view(), name='playlist_share'),
    path('criar/', PlaylistCreateView.as_view(), name='criar_playlist'),
    path('<int:pk>/atualizar-tempo/', atualizar_tempo_playlist, name='atualizar_tempo_playlist'),
    path('playlist/<int:pk>/upload-capa/', PlaylistUpdateCapaView.as_view(), name='upload_capa'),
    path('playlist/<int:pk>/favoritar/', favoritar_playlist, name='favoritar_playlist'),
]