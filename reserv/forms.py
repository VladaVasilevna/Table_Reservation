from django import forms
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField

from .models import Reservation


class BookingForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите имя",
                "id": "name",
                "required": True,
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите email",
                "id": "email",
                "required": True,
            }
        )
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите телефон",
                "id": "phone",
                "required": True,
            }
        ),
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "placeholder": "Дата",
                "id": "date",
                "type": "date",
                "required": True,
            }
        )
    )
    time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "class": "form-control",
                "placeholder": "Время",
                "id": "time",
                "type": "time",
                "required": True,
            }
        )
    )
    people = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Кол-во гостей",
                "id": "people",
                "required": True,
            }
        ),
    )
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Комментарий",
                "rows": 5,
            }
        ),
    )


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите имя",
                "id": "name",
                "required": True,
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите email",
                "id": "email",
                "required": True,
            }
        )
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Тема сообщения",
                "id": "subject",
                "required": True,
            }
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Сообщение",
                "required": True,
                "rows": 5,
            }
        )
    )


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


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["date", "time", "guests", "comment"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "guests": forms.NumberInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
