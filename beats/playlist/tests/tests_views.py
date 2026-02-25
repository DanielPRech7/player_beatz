from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from model_bakery import baker
from beats.playlist.models import Playlist, Song, PlaylistProgress
from beats.friendships.models import Friendship
from django.core import mail

User = get_user_model()

class PlaylistViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = baker.make(User, username='dj_khaled')
        self.user.set_password('pass123')
        self.user.save()
        
        self.songs = baker.make(Song, _quantity=3)
        self.playlist = baker.make(Playlist, name="Summer Vibes")
        self.playlist.songs.set(self.songs)
        
        self.detail_url = reverse('playlist_detail', kwargs={'pk': self.playlist.pk})
        self.favorite_url = reverse('favorite_playlist', kwargs={'pk': self.playlist.pk})
        self.update_time_url = reverse('update_playlist_time', kwargs={'pk': self.playlist.pk})

    def test_favorite_playlist_ajax(self):
        self.client.login(username='dj_khaled', password='pass123')
        response = self.client.post(self.favorite_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['favorite'])
        self.assertIn(self.user, self.playlist.favorites.all())
        response = self.client.post(self.favorite_url)
        self.assertEqual(response.json()['favorite'], False)
        self.assertNotIn(self.user, self.playlist.favorites.all())

    def test_update_playlist_time_f_expression(self):
        self.client.login(username='dj_khaled', password='pass123')
        response = self.client.post(self.update_time_url, {'seconds': 30})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total_accumulated'], 30)
        response = self.client.post(self.update_time_url, {'seconds': 20})
        self.assertEqual(response.json()['total_accumulated'], 50)

    def test_playlist_detail_view_context_with_friends(self):
        self.client.login(username='dj_khaled', password='pass123')
        friend = baker.make(User, username='anitta')
        baker.make(Friendship, from_user=self.user, to_user=friend, status=Friendship.Status.ACCEPTED)
        friend_playlist = baker.make(Playlist, name="Anitta Hits")
        baker.make(PlaylistProgress, user=friend, playlist=friend_playlist)
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['last_friend_playlist'], friend_playlist)

    def test_playlist_share_email(self):
        self.client.login(username='dj_khaled', password='pass123')
        share_url = reverse('playlist_share', kwargs={'pk': self.playlist.pk})
        response = self.client.post(share_url, {'email': 'test@example.com'})
        
        self.assertRedirects(response, self.detail_url)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Summer Vibes", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])