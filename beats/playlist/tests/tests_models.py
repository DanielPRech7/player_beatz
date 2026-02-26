from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from model_bakery import baker
from beats.playlist.models import Song, Playlist, PlaylistProgress

User = get_user_model()

class PlaylistModelsTestCase(TestCase):

    def test_song_creation(self):
        song = baker.make(Song, title="Bohemian Rhapsody", artist="Queen")
        self.assertEqual(str(song), "Bohemian Rhapsody - Queen")
        self.assertTrue(isinstance(song, Song))

    def test_playlist_with_songs_and_favorites(self):
        songs = baker.make(Song, _quantity=3)
        users = baker.make(User, _quantity=2)
        
        playlist = baker.make(Playlist, name="My Awesome List")
        playlist.songs.set(songs)
        playlist.favorites.set(users)

        self.assertEqual(playlist.songs.count(), 3)
        self.assertEqual(playlist.favorites.count(), 2)
        self.assertEqual(str(playlist), "My Awesome List")

    def test_playlist_progress_logic(self):
        user = baker.make(User)
        playlist = baker.make(Playlist)
        
        progress = baker.make(
            PlaylistProgress, 
            user=user, 
            playlist=playlist, 
            seconds_watched=120
        )

        self.assertEqual(
            str(progress), 
            f"{user.username} - {playlist.name}: 120s"
        )

    def test_unique_together_progress(self):
        user = baker.make(User)
        playlist = baker.make(Playlist)
        
        baker.make(PlaylistProgress, user=user, playlist=playlist)

        with self.assertRaises(IntegrityError):
            baker.make(PlaylistProgress, user=user, playlist=playlist)