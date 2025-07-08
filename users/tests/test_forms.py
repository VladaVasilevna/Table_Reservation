from django.contrib.auth import get_user_model
from django.test import TestCase

from ..forms import UserLoginForm, UserRegistrationForm

User = get_user_model()


class UserRegistrationFormTest(TestCase):
    """Тесты для формы регистрации пользователя"""

    def test_registration_form_valid(self):
        """Тест валидной формы регистрации"""
        form_data = {
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_email(self):
        """Тест невалидной формы с неправильным email"""
        form_data = {
            "email": "invalid-email",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registration_form_passwords_dont_match(self):
        """Тест невалидной формы с несовпадающими паролями"""
        form_data = {
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "differentpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_weak_password(self):
        """Тест невалидной формы со слабым паролем"""
        form_data = {
            "email": "test@example.com",
            "password1": "123",
            "password2": "123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_save(self):
        """Тест сохранения пользователя через форму"""
        form_data = {
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))


class UserLoginFormTest(TestCase):
    """Тесты для формы входа пользователя"""

    def setUp(self):
        """Создаем тестового пользователя"""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_login_form_valid(self):
        """Тест валидной формы входа"""
        form_data = {"email": "test@example.com", "password": "testpass123"}
        form = UserLoginForm(data=form_data)
        # Форма должна быть валидной по полям, но не проверяет аутентификацию
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_email(self):
        """Тест невалидной формы с неправильным email"""
        form_data = {"email": "invalid-email", "password": "testpass123"}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_login_form_empty_password(self):
        """Тест невалидной формы с пустым паролем"""
        form_data = {"email": "test@example.com", "password": ""}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_login_form_empty_email(self):
        """Тест невалидной формы с пустым email"""
        form_data = {"email": "", "password": "testpass123"}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
