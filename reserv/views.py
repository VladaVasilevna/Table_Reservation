
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import BookingForm, ContactForm, RegistrationForm, ReservationForm
from .models import Reservation


def home(request):
    booking_form = BookingForm()
    contact_form = ContactForm()
    print("0")
    if request.method == "POST":
        # Определяем, какая форма была отправлена по имени кнопки submit или скрытому полю
        if "booking_submit" in request.POST:
            print("1")
            booking_form = BookingForm(request.POST)
            if booking_form.is_valid():
                print("2")
                send_mail(
                    "Новое бронирование",
                    f"Детали бронирования:\n{booking_form.cleaned_data}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    "Ваш запрос на бронирование успешно отправлен! "
                    "Мы свяжемся с вами в ближайшее время. Спасибо, что выбрали Savor!",
                )
                return redirect("home")
        elif "contact_submit" in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                send_mail(
                    contact_form.cleaned_data["subject"],
                    contact_form.cleaned_data["message"],
                    contact_form.cleaned_data["email"],
                    [settings.DEFAULT_FROM_EMAIL],
                )
                messages.success(
                    request,
                    "Ваше сообщение успешно отправлено! Спасибо за обратную связь.",
                )
                return redirect("home")

    return render(
        request,
        "reserv/index.html",
        {
            "booking_form": booking_form,
            "contact_form": contact_form,
        },
    )


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "reserv/register.html", {"form": form})


@login_required
def profile(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, "reserv/profile.html", {"reservations": reservations})


@login_required
def create_reservation(request):
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            messages.success(request, "Бронь успешно создана!")
            return redirect("profile")
    else:
        form = ReservationForm()
    return render(request, "reserv/reservation.html", {"form": form})
