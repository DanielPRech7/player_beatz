from django.db import models
from django.contrib.auth.models import User

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=11, unique=True)
    def __str__(self):
        return f"{self.title} - {self.artist}"

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    songs = models.ManyToManyField(Song, related_name='playlists')
    cover = models.ImageField(upload_to='capas_playlists/', null=True, blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_playlists', blank=True)

    def __str__(self):
        return self.name

class PlaylistProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    seconds_watched = models.PositiveIntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'playlist')

    def __str__(self):
        return f"{self.user.username} - {self.playlist.name}: {self.seconds_watched}s"

