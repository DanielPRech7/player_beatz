from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from beats.core.views import BaseDetailView

class TestBaseDetailViewNoDB(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')
        self.factory = RequestFactory()

    def test_detail_view_mocked_object(self):
        fake_obj = type('FakeObj', (), {'nome': 'Objeto Fake'})()

        class TestView(BaseDetailView):
            template_name = 'core/test_detail.html'
            def get_object(self):
                return fake_obj

        request = self.factory.get('/fake-url/')
        request.user = self.user

        view = TestView.as_view()
        response = view(request, pk=1)

        self.assertEqual(response.status_code, 200)
