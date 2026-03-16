from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from model_bakery import baker  # Importação da biblioteca
from beats.friendships.models import Friendship

User = get_user_model()

class FriendshipViewsTestCase(TestCase):
    def setUp(self):
        self.user1 = baker.make(User, username='joao')
        self.user2 = baker.make(User, username='maria')
        self.user3 = baker.make(User, username='jose')
        
        for user in [self.user1, self.user2, self.user3]:
            user.set_password('password123')
            user.save()

        self.lista_url = reverse('friendships:lista')

    def test_lista_usuarios_view_requires_login(self):
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, 302)

    def test_lista_usuarios_conteudo(self):
        self.client.login(username='joao', password='password123')
        response = self.client.get(self.lista_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user1, response.context['todos_usuarios'])
        self.assertIn(self.user2, response.context['todos_usuarios'])
        self.assertIn(self.user3, response.context['todos_usuarios'])

    def test_adicionar_amigo_sucesso(self):
        self.client.login(username='joao', password='password123')
        url = reverse('friendships:adicionar', kwargs={'pk': self.user2.pk})
        
        response = self.client.post(url)
        
        self.assertEqual(Friendship.objects.count(), 1)
        friendship = Friendship.objects.first()
        self.assertEqual(friendship.from_user, self.user1)
        self.assertEqual(friendship.to_user, self.user2)
        self.assertEqual(friendship.status, Friendship.Status.PENDING)
        self.assertRedirects(response, self.lista_url)

    def test_responder_solicitacao_aceitar(self):
        solicitacao = baker.make(Friendship, from_user=self.user2, to_user=self.user1)
        
        self.client.login(username='joao', password='password123')
        url = reverse('friendships:responder', kwargs={'pk': solicitacao.pk})
        
        response = self.client.post(url, {'acao': 'aceitar'})
        
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, Friendship.Status.ACCEPTED)

    def test_responder_solicitacao_alheia_erro(self):
        solicitacao = baker.make(Friendship, from_user=self.user1, to_user=self.user2)
        
        self.client.login(username='jose', password='password123')
        url = reverse('friendships:responder', kwargs={'pk': solicitacao.pk})
        
        response = self.client.post(url, {'acao': 'aceitar'})
        self.assertEqual(response.status_code, 404)