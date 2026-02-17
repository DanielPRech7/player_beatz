from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Musica(models.Model):
    titulo = models.CharField(max_length=200)
    artista = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=11, unique=True) 
    def __str__(self):
        return f"{self.titulo} - {self.artista}"

class Playlist(models.Model):
    nome = models.CharField(max_length=200)
    musicas = models.ManyToManyField(Musica, related_name='playlists')
    capa = models.ImageField(upload_to='capas_playlists/', null=True, blank=True)
    favoritos = models.ManyToManyField(User, related_name='playlists_favoritas', blank=True)
    
    def media_avaliacoes(self):
        avaliacoes = self.playlistrating_set.all()
        if avaliacoes:
            return sum(avaliacao.nota for avaliacao in avaliacoes) / avaliacoes.count()
        return 0
    
    def __str__(self):
        return self.nome

class PlaylistProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    segundos_assistidos = models.PositiveIntegerField(default=0)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'playlist')

    def __str__(self):
        return f"{self.user.username} - {self.playlist.nome}: {self.segundos_assistidos}s"

class PlaylistRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    nota = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'playlist')

    def __str__(self):
        return f"{self.user.username} - {self.playlist.nome} - {self.nota}"