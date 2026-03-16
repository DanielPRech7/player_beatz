from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile # Import necessário
from beats.profiles.models import Profile


class ProfileModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='password123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            bio='Minha bio de teste'
        )

    def test_str(self):
        self.assertEqual(str(self.profile), 'testuser')

    def test_create_with_duplicate_user(self):
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user, bio='Segunda bio')

    def test_profile_bio_content(self):
        self.assertEqual(self.profile.bio, 'Minha bio de teste')

    def test_profile_avatar_upload_path(self):
        avatar_file = SimpleUploadedFile(
            name='foto.jpg', 
            content=b'file_content', 
            content_type='image/jpeg'
        )
        
        self.profile.avatar = avatar_file
        self.profile.save()
        expected_path = f'profiles/avatars/{self.user.pk}/foto.jpg'
        self.assertEqual(self.profile.avatar.name, expected_path)