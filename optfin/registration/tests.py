from django.test import TestCase
from registration.models import User

class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            login="testuser",
            email="testuser@example.com",
            password_hash="123456"
        )

    def test_create_user(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)
        self.assertEqual(self.user.login, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")

    def test_update_user(self):
        self.user.login = "updateduser"
        self.user.email = "updated@example.com"
        self.user.save()

        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.login, "updateduser")
        self.assertEqual(updated_user.email, "updated@example.com")

    def test_delete_user(self):
        user_id = self.user.id
        self.user.delete()
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)

