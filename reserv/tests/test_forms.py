from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ..forms import ContactForm, ModalBookingForm, ReservationForm
from ..models import Settings, Table

User = get_user_model()


class ReservationFormTest(TestCase):
    """Тесты для формы ReservationForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )
        self.table = Table.objects.create(
            number=1, capacity=4, shape="round", x=100, y=100, width=60, height=60
        )
        self.settings = Settings.get_settings()

    def test_reservation_form_valid(self):
        """Тест валидной формы бронирования"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            "date": tomorrow,
            "time": "12:00",
            "guests": 2,
            "comment": "Test reservation",
        }
        form = ReservationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_reservation_form_invalid_date_past(self):
        """Тест невалидной формы с прошедшей датой"""
        yesterday = timezone.now().date() - timedelta(days=1)
        form_data = {"date": yesterday, "time": "12:00", "guests": 2}
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date", form.errors)

    def test_reservation_form_invalid_time_before_open(self):
        """Тест невалидной формы с временем до открытия"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            "date": tomorrow,
            "time": "10:00",  # До открытия в 11:00
            "guests": 2,
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("time", form.errors)

    def test_reservation_form_invalid_time_after_last_booking(self):
        """Тест невалидной формы с временем после последнего бронирования"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            "date": tomorrow,
            "time": "23:00",  # После последнего бронирования в 22:00
            "guests": 2,
        }
        form = ReservationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("time", form.errors)


class ModalBookingFormTest(TestCase):
    """Тесты для формы ModalBookingForm"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123", full_name="Test User"
        )

    def test_modal_booking_form_valid(self):
        """Тест валидной модальной формы бронирования"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "date": tomorrow,
            "time": "12:00",
            "guests": 2,
            "comment": "Test reservation",
        }
        form = ModalBookingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_modal_booking_form_fields_readonly(self):
        """Тест что поля даты и времени только для чтения"""
        form = ModalBookingForm()
        self.assertIn("readonly", str(form["date"]))
        self.assertIn("readonly", str(form["time"]))

    def test_modal_booking_form_initial_values(self):
        """Тест начальных значений формы"""
        tomorrow = timezone.now().date() + timedelta(days=1)
        form = ModalBookingForm(initial={"date": tomorrow, "time": "12:00"})
        self.assertEqual(form.initial["date"], tomorrow)
        self.assertEqual(form.initial["time"], "12:00")


class ContactFormTest(TestCase):
    """Тесты для формы ContactForm"""

    def test_contact_form_valid(self):
        """Тест валидной формы обратной связи"""
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "Test message content",
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid_email(self):
        """Тест невалидной формы с неправильным email"""
        form_data = {
            "name": "Test User",
            "email": "invalid-email",
            "subject": "Test Subject",
            "message": "Test message content",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"][0], "Введите правильный адрес электронной почты.")

    def test_contact_form_empty_message(self):
        """Тест невалидной формы с пустым сообщением"""
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)
