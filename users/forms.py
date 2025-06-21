from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import BooleanField, ClearableFileInput, ModelForm, TextInput

from users.choices import COUNTRY_CHOICES
from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class UserProfileForm(StyleFormMixin, ModelForm):
    country = forms.ChoiceField(
        choices=[("", "---------")] + COUNTRY_CHOICES,
        required=False,
        label="Страна",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["full_name", "phone_number", "country", "avatar"]
        widgets = {
            "full_name": TextInput(
                attrs={"class": "form-control", "placeholder": "Введите имя"}
            ),
            "phone_number": TextInput(
                attrs={"class": "form-control", "placeholder": "Введите номер телефона"}
            ),
            "avatar": ClearableFileInput(attrs={"class": "form-control"}),
        }
