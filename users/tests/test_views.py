from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserRegistrationViewTest(TestCase):
    """Тесты для представления регистрации пользователя"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse("users:register")

    def test_register_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/user_form.html")
        self.assertIn("form", response.context)

    def test_register_view_post_valid(self):
        """Тест POST запроса с валидными данными"""
        form_data = {
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.register_url, data=form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Редирект после успешной регистрации

        # Проверяем что пользователь создан
        user = User.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(user)
        # Не проверяем full_name, так как оно не требуется при регистрации

    def test_register_view_post_invalid(self):
        """Тест POST запроса с невалидными данными"""
        form_data = {
            "email": "invalid-email",
            "password1": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.register_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())

    def test_register_view_duplicate_email(self):
        """Тест регистрации с уже существующим email"""
        # Создаем первого пользователя
        User.objects.create_user(email="test@example.com", password="testpass123")

        # Пытаемся создать второго с тем же email
        form_data = {
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }

        response = self.client.post(self.register_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками

        # Проверяем что второй пользователь не создан
        users = User.objects.filter(email="test@example.com")
        self.assertEqual(users.count(), 1)


class UserLoginViewTest(TestCase):
    """Тесты для представления входа пользователя"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse("users:login")
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_login_view_get(self):
        """Тест GET запроса к странице входа"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/registration/login.html")
        self.assertIn("form", response.context)

    def test_login_view_post_valid(self):
        """Тест POST запроса с валидными данными"""
        form_data = {"email": "test@example.com", "password": "testpass123"}

        response = self.client.post(self.login_url, data=form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа

        # Проверяем что пользователь аутентифицирован
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.email, "test@example.com")

    def test_login_view_post_invalid_credentials(self):
        """Тест POST запроса с неверными учетными данными"""
        form_data = {"email": "test@example.com", "password": "wrongpassword"}

        response = self.client.post(self.login_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertIn("form", response.context)

        # Проверяем что пользователь не аутентифицирован
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)

    def test_login_view_post_nonexistent_user(self):
        """Тест POST запроса с несуществующим пользователем"""
        form_data = {"email": "nonexistent@example.com", "password": "testpass123"}

        response = self.client.post(self.login_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками

        # Проверяем что пользователь не аутентифицирован
        user = response.wsgi_request.user
        self.assertFalse(user.is_authenticated)


class UserLogoutViewTest(TestCase):
    """Тесты для представления выхода пользователя"""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse("users:logout")
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_logout_view_authenticated_user(self):
        """Тест выхода аутентифицированного пользователя"""
        # Сначала входим
        self.client.login(email="test@example.com", password="testpass123")

        # Проверяем что пользователь аутентифицирован
        response = self.client.get(reverse("reserv:index"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        # Выходим
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Редирект после выхода

        # Проверяем что пользователь больше не аутентифицирован
        response = self.client.get(reverse("reserv:index"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_view_unauthenticated_user(self):
        """Тест выхода неаутентифицированного пользователя"""
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Редирект


class PasswordResetViewTest(TestCase):
    """Тесты для представления сброса пароля"""

    def setUp(self):
        self.client = Client()
        self.password_reset_url = reverse("users:password_reset")
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_password_reset_view_get(self):
        """Тест GET запроса к странице сброса пароля"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/password_reset_form.html")

    def test_password_reset_view_post_valid_email(self):
        """Тест POST запроса с валидным email"""
        form_data = {"email": "test@example.com"}

        response = self.client.post(self.password_reset_url, data=form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Редирект на страницу подтверждения

        # Проверяем что письмо отправлено
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], "test@example.com")

    def test_password_reset_view_post_invalid_email(self):
        """Тест POST запроса с невалидным email"""
        form_data = {"email": "invalid-email"}

        response = self.client.post(self.password_reset_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками

        # Проверяем что письмо не отправлено
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_view_post_nonexistent_email(self):
        """Тест POST запроса с несуществующим email"""
        form_data = {"email": "nonexistent@example.com"}

        response = self.client.post(self.password_reset_url, data=form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Редирект на страницу подтверждения

        # Проверяем что письмо не отправлено (для безопасности)
        self.assertEqual(len(mail.outbox), 0)
