import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import ContactMessage, Reservation, Settings, Table

User = get_user_model()


class BookingFlowIntegrationTest(TestCase):
    """Интеграционные тесты для полного процесса бронирования"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.table = Table.objects.create(
            number=1, capacity=4, shape="round", x=100, y=100, width=60, height=60
        )
        self.settings = Settings.get_settings()

    def test_complete_booking_flow(self):
        """Тест полного процесса бронирования"""
        # Аутентифицируем пользователя
        self.client.login(email="test@example.com", password="testpass123")

        # 1. Проверяем что стол доступен
        response = self.client.get(reverse("reserv:get_tables"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        table_data = next((t for t in data["tables"] if t["id"] == self.table.id), None)
        self.assertTrue(table_data["is_available"])

        # 2. Создаем бронирование
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "date": tomorrow,
            "time": "12:00",
            "guests": 2,
            "comment": "Test reservation",
            "table_id": self.table.id,  # Добавляем table_id
        }

        response = self.client.post(reverse("reserv:book_table"), data=form_data)
        self.assertEqual(response.status_code, 302)

        # 3. Проверяем что бронирование создано
        reservation = Reservation.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.status, "pending")

        # 4. Проверяем что стол стал недоступен
        response = self.client.get(
            reverse("reserv:get_tables"),
            {"date": tomorrow.strftime("%Y-%m-%d"), "time": "12:00"},
        )
        data = json.loads(response.content)
        table_data = next((t for t in data["tables"] if t["id"] == self.table.id), None)
        self.assertFalse(table_data["is_available"])

    def test_booking_conflict_prevention(self):
        """Тест предотвращения конфликтов бронирования"""
        # Аутентифицируем пользователя
        self.client.login(email="test@example.com", password="testpass123")

        tomorrow = timezone.now().date() + timedelta(days=1)

        # Создаем первое бронирование
        Reservation.objects.create(
            user=self.user,
            table=self.table,
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            date=tomorrow,
            time=datetime.strptime("12:00", "%H:%M").time(),
            guests=2,
            duration_hours=2,
        )

        # Пытаемся создать второе бронирование в то же время
        form_data = {
            "name": "User 2",
            "email": "user2@example.com",
            "phone": "+1234567891",
            "date": tomorrow,
            "time": "13:00",  # Пересекается с первым бронированием
            "guests": 2,
            "table_id": self.table.id,  # Добавляем table_id
        }

        response = self.client.post(reverse("reserv:book_table"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect при конфликте

        # Проверяем что второе бронирование не создано
        reservation2 = Reservation.objects.filter(email="user2@example.com").first()
        self.assertIsNone(reservation2)

    def test_settings_integration(self):
        """Тест интеграции настроек с процессом бронирования"""
        # Аутентифицируем пользователя
        self.client.login(email="test@example.com", password="testpass123")

        # Изменяем настройки
        self.settings.booking_duration_hours = 3
        self.settings.restaurant_open_time = datetime.strptime("10:00", "%H:%M").time()
        self.settings.restaurant_close_time = datetime.strptime("22:00", "%H:%M").time()
        self.settings.last_booking_time = datetime.strptime("20:00", "%H:%M").time()
        self.settings.save()

        # Проверяем что настройки применяются в API
        response = self.client.get(reverse("reserv:settings_api"))
        data = json.loads(response.content)
        self.assertEqual(data["booking_duration_hours"], 3)
        self.assertEqual(data["restaurant_open_time"], "10:00")
        self.assertEqual(data["restaurant_close_time"], "22:00")
        self.assertEqual(data["last_booking_time"], "20:00")

        # Проверяем что настройки применяются при бронировании
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "date": tomorrow,
            "time": "09:00",  # До открытия
            "guests": 2,
            "table_id": self.table.id,  # Добавляем table_id
        }

        response = self.client.post(reverse("reserv:book_table"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect при ошибке валидации


class ContactFlowIntegrationTest(TestCase):
    """Интеграционные тесты для процесса обратной связи"""

    def setUp(self):
        self.client = Client()

    def test_contact_form_submission_flow(self):
        """Тест полного процесса отправки формы обратной связи"""
        # 1. Открываем страницу контактов
        response = self.client.get(reverse("reserv:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

        # 2. Отправляем форму
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message content",
        }

        response = self.client.post(reverse("reserv:contact"), data=form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешной отправки

        # 3. Проверяем что сообщение создано
        message = ContactMessage.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(message)
        self.assertEqual(message.name, "Test User")
        self.assertEqual(message.subject, "Test Subject")
        self.assertFalse(message.is_read)


class UserAuthenticationIntegrationTest(TestCase):
    """Интеграционные тесты для аутентификации пользователей"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_login_logout_flow(self):
        """Тест процесса входа и выхода"""
        # 1. Пытаемся войти с неправильными данными
        login_data = {"email": "test@example.com", "password": "wrongpassword"}
        response = self.client.post(reverse("users:login"), data=login_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками

        # 2. Входим с правильными данными
        login_data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(reverse("users:login"), data=login_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа

        # 3. Проверяем что пользователь аутентифицирован
        response = self.client.get(reverse("reserv:index"))
        self.assertEqual(response.status_code, 200)

        # 4. Выходим
        response = self.client.get(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
