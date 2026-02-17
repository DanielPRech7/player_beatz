from django.test import TestCase, Client
from django.urls import reverse
from beats.playlist.models import Playlist

class PlaylistViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.playlist = Playlist.objects.create(nome="Playlist Teste")

    def test_playlist_list_view(self):
        url = reverse('playlist_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'playlist/playlist_list.html')
        self.assertIn(self.playlist, response.context['playlists'])

    def test_playlist_detail_view(self):
        url = reverse('playlist_detail', args=[self.playlist.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'playlist/playlist_detail.html')
        self.assertEqual(response.context['playlist'], self.playlist)

    def test_playlist_create_view(self):
        url = reverse('criar_playlist')
        data = {'nome': 'Nova Playlist'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Playlist.objects.filter(nome='Nova Playlist').exists())
