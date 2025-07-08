from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты для модели User"""

    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.full_name, "Test User")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_creation_without_email(self):
        """Тест создания пользователя без email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="", password="testpass123", full_name="Test User"
            )

    def test_superuser_creation(self):
        """Тест создания суперпользователя"""
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123", full_name="Admin User"
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.assertEqual(str(user), "test@example.com")

    def test_user_email_unique(self):
        """Тест уникальности email"""
        User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

        with self.assertRaises(Exception):  # IntegrityError или ValidationError
            User.objects.create_user(
                email="test@example.com",
                password="testpass123",
                full_name="Another User",
            )

    def test_user_avatar_upload(self):
        """Тест загрузки аватара"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

        # Проверяем что аватар по умолчанию установлен
        self.assertIsNotNone(user.avatar)

    def test_user_get_full_name(self):
        """Тест получения полного имени"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.assertEqual(user.get_full_name(), "Test User")

    def test_user_get_short_name(self):
        """Тест получения короткого имени"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.assertEqual(user.get_short_name(), "Test User")
