from django.contrib.auth.models import User
from django.test import TestCase


class ProfileModelTest(TestCase):
    def test_profile_created_on_user_creation(self):
        u = User.objects.create_user(username="alice", password="pass")
        self.assertTrue(hasattr(u, "profile"))
        self.assertEqual(u.profile.user, u)
