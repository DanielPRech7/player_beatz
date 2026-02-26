from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from beats.friendships.models import Friendship

User = get_user_model()

class FriendshipModelsTest(TestCase):

    def setUp(self):
        self.user_sender = User.objects.create_user(username='sender', password='password123')
        self.user_receiver = User.objects.create_user(username='receiver', password='password123')
        
        self.friendship = Friendship.objects.create(
            from_user=self.user_sender,
            to_user=self.user_receiver
        )

    def test_str(self):
        expected_str = f"sender -> receiver (Pending)"
        self.assertEqual(str(self.friendship), expected_str)

    def test_default_status_is_pending(self):
        self.assertEqual(self.friendship.status, Friendship.Status.PENDING)
        self.assertFalse(self.friendship.is_accepted)

    def test_accept_method(self):
        self.friendship.accept()
        self.assertEqual(self.friendship.status, Friendship.Status.ACCEPTED)
        self.assertTrue(self.friendship.is_accepted)

    def test_reject_method(self):
        self.friendship.reject()
        self.assertEqual(self.friendship.status, Friendship.Status.REJECTED)
        self.assertFalse(self.friendship.is_accepted)

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            Friendship.objects.create(
                from_user=self.user_sender,
                to_user=self.user_receiver
            )

    def test_reverse_friendship_allowed(self):
        reverse = Friendship.objects.create(
            from_user=self.user_receiver,
            to_user=self.user_sender
        )
        self.assertIsNotNone(reverse.pk)