from django.conf import settings
from django.db import models


class Table(models.Model):
    """Модель столиков"""

    number = models.PositiveIntegerField(unique=True, verbose_name="Номер столика")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость (чел)")
    shape = models.CharField(max_length=10, choices=[('round', 'Круглый'), ('rect', 'Прямоугольный')], verbose_name="Форма столика")
    x = models.IntegerField(verbose_name="Координата по X")  # координата на схеме
    y = models.IntegerField(verbose_name="Координата по Y")
    width = models.IntegerField(verbose_name="Ширина кнопки")
    height = models.IntegerField(verbose_name="Высота кнопки")
    is_active = models.BooleanField(default=True, verbose_name="Доступен")

    class Meta:
        verbose_name = "Столик"
        verbose_name_plural = "Столики"

    def __str__(self):
        return f"Столик №{self.number} ({self.capacity} чел)"


class Reservation(models.Model):
    """Модель бронирований"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    table = models.ForeignKey(
        'Table',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name="Столик"
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    guests = models.PositiveIntegerField(verbose_name="Количество гостей")
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
        return f"Бронь #{self.id} - {self.user.username}"
