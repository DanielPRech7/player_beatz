from django.test import TestCase
from django.db.utils import IntegrityError
from beats.playlist.models import Musica, Playlist 


class MusicaPlaylistModelsTest(TestCase):

    def setUp(self):
        self.musica_1 = Musica.objects.create(
            titulo='Stairway to Heaven', 
            artista='Led Zeppelin', 
            youtube_id='QjH_E_o_qS4'
        )
        self.musica_2 = Musica.objects.create(
            titulo='Bohemian Rhapsody', 
            artista='Queen', 
            youtube_id='fJ9rUzIMcZQ'
        )

        self.playlist_rock = Playlist.objects.create(nome='Classic Rock Hits')

        self.playlist_rock.musicas.add(self.musica_1, self.musica_2)

    def test_musica_str_representation(self):
        """Testa se o método __str__ de Musica retorna 'Título - Artista'."""
        expected_str = 'Stairway to Heaven - Led Zeppelin'
        self.assertEqual(str(self.musica_1), expected_str)

    def test_musica_youtube_id_is_unique(self):
        """Testa se tentar criar uma Música com um youtube_id duplicado falha."""
        with self.assertRaises(IntegrityError):
            Musica.objects.create(
                titulo='Fake Song', 
                artista='Fake Artist', 
                youtube_id='QjH_E_o_qS4'
            )

    def test_playlist_str_representation(self):
        """Testa se o método __str__ de Playlist retorna o nome da playlist."""
        self.assertEqual(str(self.playlist_rock), 'Classic Rock Hits')

    def test_playlist_many_to_many_relationship(self):
        """Testa se a Playlist contém as Músicas corretas."""
        self.assertEqual(self.playlist_rock.musicas.count(), 2)

        self.assertIn(self.musica_1, self.playlist_rock.musicas.all())

    def test_musica_reverse_relationship(self):
        """Testa se a música sabe a quais Playlists ela pertence."""
        self.assertIn(self.playlist_rock, self.musica_2.playlists.all())

        playlist_2 = Playlist.objects.create(nome='Favorites')
        playlist_2.musicas.add(self.musica_2)

        self.assertEqual(self.musica_2.playlists.count(), 2)