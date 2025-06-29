import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..forms import ReservationForm
from ..models import ContactMessage, Reservation, Table

User = get_user_model()


class IndexViewTest(TestCase):
    """Тесты для главной страницы"""

    def setUp(self):
        self.client = Client()
        self.index_url = reverse("reserv:index")
        self.table = Table.objects.create(
            number=1, capacity=4, shape="round", x=100, y=100, width=60, height=60
        )

    def test_index_view_get(self):
        """Тест GET запроса к главной странице"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reserv/index.html")
        self.assertIn("tables", response.context)
        self.assertIn("form", response.context)

    def test_index_view_context_data(self):
        """Тест контекстных данных главной страницы"""
        response = self.client.get(self.index_url)
        self.assertIsInstance(response.context["form"], ReservationForm)
        self.assertIn(self.table, response.context["tables"])


class GetTablesViewTest(TestCase):
    """Тесты для API получения столов"""

    def setUp(self):
        self.client = Client()
        self.get_tables_url = reverse("reserv:get_tables")
        self.table = Table.objects.create(
            number=1, capacity=4, shape="round", x=100, y=100, width=60, height=60
        )
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_get_tables_view_get(self):
        """Тест GET запроса для получения столов"""
        response = self.client.get(self.get_tables_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("tables", data)
        self.assertIn("settings", data)

    def test_get_tables_with_reservation(self):
        """Тест получения столов с существующим бронированием"""
        tomorrow = timezone.now().date() + timedelta(days=1)
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

        # Вызываем API с параметрами даты и времени, соответствующими бронированию
        response = self.client.get(
            self.get_tables_url,
            {"date": tomorrow.strftime("%Y-%m-%d"), "time": "12:00"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        tables_data = data["tables"]

        # Находим наш стол в данных
        table_data = next((t for t in tables_data if t["id"] == self.table.id), None)
        self.assertIsNotNone(table_data)
        self.assertFalse(table_data["is_available"])


class BookTableViewTest(TestCase):
    """Тесты для бронирования стола"""

    def setUp(self):
        self.client = Client()
        self.book_table_url = reverse("reserv:book_table")
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.table = Table.objects.create(
            number=1, capacity=4, shape="round", x=100, y=100, width=60, height=60
        )

    def test_book_table_view_get(self):
        """Тест GET запроса к странице бронирования - должен делать redirect"""
        # Аутентифицируем пользователя
        self.client.login(email="test@example.com", password="testpass123")
        response = self.client.get(self.book_table_url)
        self.assertEqual(response.status_code, 302)  # Redirect на главную страницу
        self.assertRedirects(response, reverse("reserv:index"))

    def test_book_table_view_post_valid(self):
        """Тест POST запроса с валидными данными"""
        # Аутентифицируем пользователя
        self.client.login(email="test@example.com", password="testpass123")

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

        response = self.client.post(self.book_table_url, data=form_data)
        self.assertEqual(
            response.status_code, 302
        )  # Редирект после успешного бронирования

        # Проверяем что бронирование создано
        reservation = Reservation.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.name, "Test User")

    def test_book_table_view_post_invalid(self):
        """Тест POST запроса с невалидными данными - должен делать redirect"""
        # Аутентифицируем пользователя
        self.client.login(email="test@example.com", password="testpass123")

        form_data = {
            "name": "Test User",
            "email": "invalid-email",
            "phone": "+1234567890",
            "date": timezone.now().date() + timedelta(days=1),
            "time": "12:00",
            "guests": 2,
            "table_id": self.table.id,  # Добавляем table_id
        }

        response = self.client.post(self.book_table_url, data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect при ошибке валидации
        self.assertRedirects(response, reverse("reserv:index"))


class ContactViewTest(TestCase):
    """Тесты для страницы контактов"""

    def setUp(self):
        self.client = Client()
        self.contact_url = reverse("reserv:contact")

    def test_contact_view_get(self):
        """Тест GET запроса к странице контактов"""
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reserv/contact.html")
        self.assertIn("form", response.context)

    def test_contact_view_post_valid(self):
        """Тест POST запроса с валидными данными"""
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message content",
        }

        response = self.client.post(self.contact_url, data=form_data)
        self.assertEqual(response.status_code, 302)  # Редирект после успешной отправки

        # Проверяем что сообщение создано
        message = ContactMessage.objects.filter(email="test@example.com").first()
        self.assertIsNotNone(message)
        self.assertEqual(message.name, "Test User")

    def test_contact_view_post_invalid(self):
        """Тест POST запроса с невалидными данными"""
        form_data = {
            "name": "Test User",
            "email": "invalid-email",
            "subject": "Test Subject",
            "message": "Test message content",
        }

        response = self.client.post(self.contact_url, data=form_data)
        self.assertEqual(response.status_code, 200)  # Возврат к форме с ошибками
        self.assertIn("form", response.context)
        self.assertFalse(response.context["form"].is_valid())


class SettingsAPIViewTest(TestCase):
    """Тесты для API настроек"""

    def setUp(self):
        self.client = Client()
        self.settings_url = reverse("reserv:settings_api")

    def test_settings_api_view_get(self):
        """Тест GET запроса к API настроек"""
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("booking_duration_hours", data)
        self.assertIn("restaurant_open_time", data)
        self.assertIn("restaurant_close_time", data)
        self.assertIn("last_booking_time", data)
