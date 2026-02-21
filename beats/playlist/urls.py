from django.urls import path
from .views import (
    PlaylistListView,
    PlaylistDetailView,
    PlaylistCreateView,
    PlaylistAddSongView,
    PlaylistShareView,
    PlaylistUpdateCoverView,
    update_playlist_time,
    favorite_playlist,
)

urlpatterns = [
    path('', PlaylistListView.as_view(), name='playlist_list'),
    path('<int:pk>/', PlaylistDetailView.as_view(), name='playlist_detail'),
    path('<int:pk>/add-song/', PlaylistAddSongView.as_view(), name='add_song_to_playlist'),
    path('<int:pk>/share/', PlaylistShareView.as_view(), name='playlist_share'),
    path('create/', PlaylistCreateView.as_view(), name='create_playlist'),
    path('<int:pk>/update-time/', update_playlist_time, name='update_playlist_time'),
    path('playlist/<int:pk>/upload-cover/', PlaylistUpdateCoverView.as_view(), name='upload_cover'),
    path('playlist/<int:pk>/favorite/', favorite_playlist, name='favorite_playlist'),
]