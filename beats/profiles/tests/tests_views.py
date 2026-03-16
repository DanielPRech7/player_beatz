from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from beats.profiles.models import Profile
from django.contrib.auth import SESSION_KEY

User = get_user_model()

class ProfileViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "password123"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        
        self.signup_url = reverse("profiles:signup")
        self.signin_url = reverse("profiles:signin")
        self.detail_url = reverse("profiles:detail")
        self.edit_url = reverse("profiles:edit")
        self.signout_url = reverse("profiles:signout")

    def test_signin_page_status_code(self):
        response = self.client.get(self.signin_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile/signin.html")

    def test_profile_detail_requires_login(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)

    def test_login_success(self):
        response = self.client.post(self.signin_url, {
            'username': self.username,
            'password': self.password
        }, follow=True)
        
        self.assertRedirects(response, self.detail_url)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.signin_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Usuário ou senha inválidos" in str(m) for m in messages))

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.signout_url)
        self.assertRedirects(response, self.signin_url)
        
        self.assertFalse(SESSION_KEY in self.client.session)

    def test_profile_update(self):
        self.client.login(username=self.username, password=self.password)
        
        new_data = {
            'first_name': 'Daniel',
            'last_name': 'Beatz',
            'bio': 'Nova bio de teste',
        }
        
        response = self.client.post(self.edit_url, new_data, follow=True)
        
        self.assertRedirects(response, self.detail_url)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Nova bio de teste')

    def test_profile_auto_creation_on_detail_view(self):
        new_user = User.objects.create_user(username="newbie", password="password")
        self.client.login(username="newbie", password="password")
        
        Profile.objects.filter(user=new_user).delete() 
        
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user=new_user).exists())