from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ..models import ContactMessage, Reservation, Settings, Table

User = get_user_model()


class TableModelTest(TestCase):
    """Тесты для модели Table"""

    def setUp(self):
        self.table = Table.objects.create(
            number=1,
            capacity=4,
            shape="round",
            x=100,
            y=100,
            width=60,
            height=60,
            is_active=True,
        )

    def test_table_creation(self):
        """Тест создания стола"""
        self.assertEqual(self.table.number, 1)
        self.assertEqual(self.table.capacity, 4)
        self.assertEqual(self.table.shape, "round")
        self.assertTrue(self.table.is_active)

    def test_table_str_representation(self):
        """Тест строкового представления стола"""
        expected = "Стол №1 (4 мест)"
        self.assertEqual(str(self.table), expected)

    def test_table_inactive(self):
        """Тест деактивации стола"""
        self.table.is_active = False
        self.table.save()
        self.assertFalse(self.table.is_active)


class SettingsModelTest(TestCase):
    """Тесты для модели Settings"""

    def test_settings_creation(self):
        """Тест создания настроек по умолчанию"""
        settings = Settings.get_settings()
        self.assertEqual(settings.booking_duration_hours, 2)
        self.assertEqual(settings.restaurant_open_time.strftime("%H:%M"), "11:00")
        self.assertEqual(settings.restaurant_close_time.strftime("%H:%M"), "23:00")
        self.assertEqual(settings.last_booking_time.strftime("%H:%M"), "22:00")

    def test_settings_str_representation(self):
        """Тест строкового представления настроек"""
        settings = Settings.get_settings()
        self.assertEqual(str(settings), "Настройки системы")

    def test_settings_singleton(self):
        """Тест что создается только один экземпляр настроек"""
        settings1 = Settings.get_settings()
        settings2 = Settings.get_settings()
        self.assertEqual(settings1.id, settings2.id)


class ReservationModelTest(TestCase):
    """Тесты для модели Reservation"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.table = Table.objects.create(
            number=1, capacity=4, shape="round", x=100, y=100, width=60, height=60
        )
        self.reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            date=timezone.now().date() + timedelta(days=1),
            time=datetime.strptime("12:00", "%H:%M").time(),
            guests=2,
            duration_hours=2,
            comment="Test reservation",
        )

    def test_reservation_creation(self):
        """Тест создания бронирования"""
        self.assertEqual(self.reservation.user, self.user)
        self.assertEqual(self.reservation.table, self.table)
        self.assertEqual(self.reservation.guests, 2)
        self.assertEqual(self.reservation.status, "pending")

    def test_reservation_str_representation(self):
        """Тест строкового представления бронирования"""
        expected = f"Бронь #{self.reservation.id} - {self.user.email}"
        self.assertEqual(str(self.reservation), expected)

    def test_get_end_time(self):
        """Тест расчета времени окончания брони"""
        end_time = self.reservation.get_end_time()
        expected_time = datetime.strptime("14:00", "%H:%M").time()
        self.assertEqual(end_time, expected_time)

    def test_get_actual_end_time_with_restaurant_close(self):
        """Тест расчета времени окончания с учетом закрытия ресторана"""
        # Создаем бронь на 22:00 (после времени закрытия кухни)
        late_reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            name="Late User",
            email="late@example.com",
            phone="+1234567890",
            date=timezone.now().date() + timedelta(days=1),
            time=datetime.strptime("22:00", "%H:%M").time(),
            guests=2,
            duration_hours=2,
        )

        # Бронь должна закончиться в 23:00 (время закрытия ресторана)
        actual_end_time = late_reservation.get_actual_end_time()
        expected_time = datetime.strptime("23:00", "%H:%M").time()
        self.assertEqual(actual_end_time, expected_time)


class ContactMessageModelTest(TestCase):
    """Тесты для модели ContactMessage"""

    def setUp(self):
        self.message = ContactMessage.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message content",
        )

    def test_contact_message_creation(self):
        """Тест создания сообщения обратной связи"""
        self.assertEqual(self.message.name, "Test User")
        self.assertEqual(self.message.email, "test@example.com")
        self.assertFalse(self.message.is_read)

    def test_contact_message_str_representation(self):
        """Тест строкового представления сообщения"""
        expected = f"Test User - Test Subject ({self.message.created_at.strftime('%d.%m.%Y %H:%M')})"
        self.assertEqual(str(self.message), expected)

    def test_contact_message_ordering(self):
        """Тест сортировки сообщений"""
        message2 = ContactMessage.objects.create(
            name="Test User 2",
            email="test2@example.com",
            subject="Test Subject 2",
            message="Test message content 2",
        )

        messages = ContactMessage.objects.all()
        self.assertEqual(messages[0], message2)  # Новое сообщение должно быть первым
