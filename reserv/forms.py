from datetime import datetime, time, timedelta

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField

from .models import ContactMessage, Reservation


class BookingForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["name", "email", "phone", "date", "time", "guests", "comment"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя",
                    "id": "name",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите email",
                    "id": "email",
                    "required": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите телефон",
                    "id": "phone",
                    "required": True,
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Дата",
                    "id": "date",
                    "type": "date",
                    "required": True,
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Время",
                    "id": "time",
                    "type": "time",
                    "required": True,
                }
            ),
            "guests": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Кол-во гостей",
                    "id": "people",
                    "required": True,
                    "min": 1,
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Комментарий",
                    "rows": 5,
                }
            ),
        }


class ModalBookingForm(forms.ModelForm):
    """Форма для модального окна с read-only полями даты и времени"""

    class Meta:
        model = Reservation
        fields = ["name", "email", "phone", "date", "time", "guests", "comment"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите email",
                    "required": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите телефон",
                    "required": True,
                }
            ),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control modal-readonly",
                    "placeholder": "Дата",
                    "type": "date",
                    "required": True,
                    "style": "background-color: #f8f9fa; cursor: not-allowed;",
                }
            ),
            "time": forms.TimeInput(
                attrs={
                    "class": "form-control modal-readonly",
                    "placeholder": "Время",
                    "type": "time",
                    "required": True,
                    "style": "background-color: #f8f9fa; cursor: not-allowed;",
                }
            ),
            "guests": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Кол-во гостей",
                    "required": True,
                    "min": 1,
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Комментарий",
                    "rows": 5,
                }
            ),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите имя",
                    "id": "name",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите email",
                    "id": "email",
                    "required": True,
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Тема сообщения",
                    "id": "subject",
                    "required": True,
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control flex-grow-1",
                    "placeholder": "Сообщение",
                    "required": True,
                    "rows": 8,
                    "style": "resize: none; min-height: 150px;",
                }
            ),
        }


class RegistrationForm(forms.ModelForm):
    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+7 (999) 123-45-67"}
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


def generate_time_choices(start="11:00", end="22:00", step_minutes=15):
    choices = []
    current = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    while current <= end_time:
        time_str = current.strftime("%H:%M")
        choices.append((time_str, time_str))
        current += timedelta(minutes=step_minutes)
    return choices


class ReservationForm(forms.ModelForm):
    time = forms.ChoiceField(
        choices=generate_time_choices(),
        widget=forms.Select(attrs={"id": "id_time", "class": "form-control"}),
    )

    class Meta:
        model = Reservation
        fields = ["date", "time", "guests", "comment"]
        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date", "id": "id_date", "class": "form-control"}
            ),
            "guests": forms.NumberInput(
                attrs={"id": "id_guests", "min": 1, "class": "form-control"}
            ),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_time(self):
        """Проверка на случай ручной подмены значения"""
        selected_str = self.cleaned_data.get("time")
        try:
            selected_time = datetime.strptime(selected_str, "%H:%M").time()
        except (ValueError, TypeError):
            raise ValidationError("Недопустимый формат времени")

        if selected_time and selected_time < time(11, 0):
            raise ValidationError(
                "Ресторан открывается в 11:00. Пожалуйста, выберите другое время."
            )
        elif selected_time and selected_time > time(22, 0):
            raise ValidationError(
                "Кухня принимает заказы до 22:00. Пожалуйста, выберите другое время."
            )
        return selected_time
