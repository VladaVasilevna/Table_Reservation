from datetime import time

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Table(models.Model):
    """Модель столов"""

    number = models.PositiveIntegerField(unique=True, verbose_name="Номер стола")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость")
    shape = models.CharField(
        max_length=20,
        choices=[
            ("round", "Круглый"),
            ("square", "Квадратный"),
            ("rectangle", "Прямоугольный"),
        ],
        default="round",
        verbose_name="Форма",
    )
    x = models.IntegerField(verbose_name="Позиция X")
    y = models.IntegerField(verbose_name="Позиция Y")
    width = models.IntegerField(verbose_name="Ширина")
    height = models.IntegerField(verbose_name="Высота")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"

    def __str__(self):
        return f"Стол №{self.number} ({self.capacity} мест)"


class Settings(models.Model):
    """Модель настроек системы"""

    booking_duration_hours = models.PositiveIntegerField(
        default=2,
        help_text="Сколько часов длится одна бронь",
        verbose_name="Продолжительность брони (часы)",
    )
    restaurant_open_time = models.TimeField(
        default=time(11, 0), verbose_name="Время открытия ресторана"
    )
    restaurant_close_time = models.TimeField(
        default=time(23, 0), verbose_name="Время закрытия ресторана"
    )
    last_booking_time = models.TimeField(
        default=time(22, 0),
        help_text="До какого времени кухня принимает заказы",
        verbose_name="Последнее время бронирования",
    )

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройки системы"

    @classmethod
    def get_settings(cls):
        """Получить настройки системы (создать по умолчанию, если не существуют)"""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                "booking_duration_hours": 2,
                "restaurant_open_time": time(11, 0),
                "restaurant_close_time": time(23, 0),
                "last_booking_time": time(22, 0),
            },
        )
        return settings


class ContactMessage(models.Model):
    """Модель сообщений обратной связи"""

    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=200, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = "Сообщение обратной связи"
        verbose_name_plural = "Сообщения обратной связи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"


class Reservation(models.Model):
    """Модель бронирований"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    table = models.ForeignKey(
        "Table",
        on_delete=models.CASCADE,
        related_name="reservations",
        verbose_name="Столик",
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    guests = models.PositiveIntegerField(verbose_name="Количество гостей")
    duration_hours = models.PositiveIntegerField(
        default=2,
        verbose_name="Продолжительность брони (часы)",
        help_text="Сколько часов длится эта бронь",
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Ожидает подтверждения"),
            ("confirmed", "Подтверждено"),
            ("canceled", "Отменено"),
        ],
        default="pending",
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронь #{self.id} - {self.user.email}"

    def get_end_time(self):
        """Получить время окончания брони"""
        from datetime import datetime, timedelta

        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + timedelta(hours=self.duration_hours)
        return end_datetime.time()

    def get_actual_end_time(self):
        """Получить фактическое время окончания брони с учетом времени закрытия ресторана"""
        from datetime import datetime, timedelta

        from .models import Settings

        start_datetime = datetime.combine(self.date, self.time)
        end_datetime = start_datetime + timedelta(hours=self.duration_hours)

        # Получаем настройки для проверки времени закрытия
        system_settings = Settings.get_settings()
        close_datetime = datetime.combine(
            self.date, system_settings.restaurant_close_time
        )

        # Если бронь заканчивается после времени закрытия, то она заканчивается в момент закрытия
        if end_datetime > close_datetime:
            return close_datetime.time()

        return end_datetime.time()
